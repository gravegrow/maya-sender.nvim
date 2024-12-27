local M = {}

M.opts = {
  host = "localhost",
  port = 5115,
  project_markers = { ".git", "pyproject.toml" },
}

local run = function(command) return vim.system({ "python", "-c", command }, {}) end

local CommandComposer = {}
CommandComposer.new = function()
  return {
    value = nil,
    append = function(self, value)
      if not value then return end
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
  local plugin_root = vim.fs.root(plugin_file, M.opts.project_markers)
  local scripts = vim.fs.joinpath(plugin_root, "scripts")

  local scripts_path = CommandComposer.new()
  scripts_path:append("import sys")
  scripts_path:append(
    string.format(
      "sys.path.append('%s') if '%s' not in sys.path else False",
      scripts,
      scripts
    )
  )
  return scripts_path.value
end

local function sender_command(command)
  command = string.gsub(command, "'", '"')
  return string.format(
    "import sender; sender.send_command('%s', ('%s', %d))",
    command,
    M.opts.host,
    M.opts.port
  )
end

local reload_project_command = function()
  return string.format("import reloader; reloader.reload('%s')", vim.fn.getcwd())
end

M.send = function(command)
  local send_command = CommandComposer.new()
  local reg_scripts = register_scripts_command()
  send_command:append(reg_scripts)
  send_command:append(sender_command(reg_scripts))
  send_command:append(sender_command(command))

  run(send_command.value)
end

local function send_file(file) M.send("exec(open('" .. file .. "').read())") end

M.send_file = function()
  local file = vim.fs.joinpath(vim.fn.getcwd(), vim.fn.expand("%"))
  M.send(reload_project_command())
  send_file(file)
end

M.send_selection = function()
  vim.fn.setreg("9", vim.fn.getreg("0")) -- store last yank in reg 9
  vim.cmd(':normal! "0y') -- yank selection
  local lines = vim.split(vim.fn.getreg("0"), "\n") -- get lines from reg 0
  vim.fn.setreg('"', vim.fn.getreg("9")) -- restore last yank from 9

  local temp_file = vim.fn.tempname()
  vim.fn.writefile(lines, temp_file)
  send_file(temp_file)
end

M.setup = function(opts)
  opts = opts or {}
  M.opts = vim.tbl_extend("force", M.opts, opts)

  vim.api.nvim_create_user_command("MayaSendBuffer", M.send_file, {})
  vim.api.nvim_create_user_command("MayaSendSelection", M.send_selection, {})
end

return M
