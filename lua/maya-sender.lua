local M = {}
M.opts = {
	host = "localhost",
	port = 5115,
}

local run = function(command)
	return vim.system({ "python", "-c", command }, {}, function(obj)
		print(obj.stderr)
		print(obj.stdout)
	end)
end

local Builder = {}
Builder.new = function()
	return {
		value = nil,
		append = function(self, value)
			if not value then
				return
			end
			if not self.value then
				self.value = value
				return
			end
			self.value = self.value .. "; " .. value
		end,
	}
end

local function register_scripts_command()
	local plugin_file = debug.getinfo(1, "S").source:sub(2)
	local plugin_root = vim.fs.root(plugin_file, { ".git" })
	local scripts = vim.fs.joinpath(plugin_root, "scripts")

	local scripts_path = Builder.new()
	scripts_path:append("import sys")
	scripts_path:append("sys.path.append('" .. scripts .. "') if '" .. scripts .. "' not in sys.path else False")
	return scripts_path.value
end

local function sender_command(command)
	command = string.gsub(command, "'", '"')
	return string.format("import sender; sender.send_command('%s', ('%s', %d))", command, M.opts.host, M.opts.port)
end

local reload_project_command = function()
	return string.format("import reloader; reloader.reload('%s')", vim.fn.getcwd())
end

M.send = function(command)
	local send_command = Builder.new()
	local reg_scripts = register_scripts_command()
	send_command:append(reg_scripts)
	send_command:append(sender_command(reg_scripts))
	send_command:append(sender_command(command))

	run(send_command.value)
end

M.send_file = function(file)
	file = file or vim.fs.joinpath(vim.fn.getcwd(), vim.fn.expand("%"))
	M.send(reload_project_command())
	M.send("exec(open('" .. file .. "').read())")
end

M.send_selection = function()
	local vstart = vim.fn.getpos("v")
	local vend = vim.fn.getpos(".")

	local line_start = vstart[2]
	local line_end = vend[2]

	local lines = vim.fn.getline(line_start, line_end)
	local temp_file = vim.fn.tempname()
	vim.fn.writefile(lines, temp_file)
	M.send_file(temp_file)
end

vim.api.nvim_create_user_command("MayaSendSelection", M.send_selection, {})
vim.api.nvim_create_user_command("MayaSendBuffer", function()
	M.send_file()
end, {})

M.setup = function(opts)
	opts = opts or {}
	vim.tbl_extend("force", M.opts, opts)
end

return M
