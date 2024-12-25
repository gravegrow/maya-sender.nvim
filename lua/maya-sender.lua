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

local function maya_command(command)
	command = string.gsub(command, "'", '"')
	return string.format("import sender; sender.send_command('%s', ('%s', %d))", command, M.opts.host, M.opts.port)
end

M.send = function(command)
	local send_command = Builder.new()
	local reg_scripts = register_scripts_command()
	send_command:append(reg_scripts)
	send_command:append(maya_command(reg_scripts))
	send_command:append(maya_command(command))

	run(send_command.value)
end

M.reload_project = function() end

M.send_buffer = function()
	-- register_scripts()
	local file = vim.fs.joinpath(vim.fn.getcwd(), vim.fn.expand("%"))
	M.send("exec(open('" .. file .. "').read())")
end

M.setup = function(opts)
	opts = opts or {}
	vim.tbl_extend("force", M.opts, opts)
end

vim.api.nvim_create_user_command("MayaSendBuffer", M.send_buffer, {})

return M
