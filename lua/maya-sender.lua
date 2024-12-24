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
		command = nil,
		append = function(self, value)
			if not value then
				return
			end
			if not self.command then
				self.command = value
				return
			end
			self.command = self.command .. "; " .. value
		end,
	}
end

M.send_command = function(command)
	local plugin_file = debug.getinfo(1, "S").source:sub(2)
	local plugin_root = vim.fs.root(plugin_file, { ".git" })
	local scripts = vim.fs.joinpath(plugin_root, "scripts/")
	local project_path = vim.fn.getcwd()

	command = string.gsub(command, "'", '"')
	command = string.format("sender.send_command('%s', ('%s', %d))", command, M.opts.host, M.opts.port)

	local builder = Builder.new()
	builder:append("import sys")
	builder:append('sys.path.append("' .. scripts .. '") if "' .. scripts .. '" not in sys.path else False')
	builder:append("import sender")
	builder:append(command)
	-- TODO: add reloader

	run(builder.command)
end

M.send_buffer = function()
	local file = vim.fs.joinpath(vim.fn.getcwd(), vim.fn.expand("%"))
	M.send_command("exec(open('" .. file .. "').read())")
end

M.setup = function(opts)
	opts = opts or {}
	vim.tbl_extend("force", M.opts, opts)
end

vim.api.nvim_create_user_command("MayaSendBuffer", M.send_buffer, {})

return M
