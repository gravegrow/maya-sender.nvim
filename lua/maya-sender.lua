local M = {}

M.opts = {
  host = "localhost",
  port = 5115,
}

local run = function(command) return vim.system({ "python", "-c", command }, {}) end

local CommandComposer = {}
CommandComposer.new = function()
  return {
    value = nil,
    append = function(self, value)
      if not self.value then
        self.value = value
        return
      end
      self.value = self.value .. "; " .. value
    end,
  }
end

local function append_path_command(path)
  local command = CommandComposer.new()
  command:append("import sys")
  command:append(
    string.format("sys.path.append('%s') if '%s' not in sys.path else False", path, path)
  )
  return command.value
end

local function register_scripts_command()
  local plugin_file = debug.getinfo(1, "S").source:sub(2)
  local plugin_root = vim.fs.root(plugin_file, { ".git", "stylua.toml" })
  local scripts = vim.fs.joinpath(plugin_root, "scripts")

  return append_path_command(scripts)
end

local function project_to_path_command(project_path)
  project_path = project_path or vim.fn.getcwd()
  return append_path_command(project_path)
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

--- @param project_path string
local reload_project_command = function(project_path)
  project_path = project_path or vim.fn.getcwd()
  return string.format("import reloader; reloader.reload('%s')", project_path)
end

M.send = function(command)
  local send_command = CommandComposer.new()
  local reg_scripts = register_scripts_command()
  send_command:append(reg_scripts)
  send_command:append(sender_command(reg_scripts))
  send_command:append(sender_command(project_to_path_command()))
  send_command:append(sender_command(command))

  run(send_command.value)
end

local function send_file(file) M.send("exec(open('" .. file .. "').read())") end

M.send_file = function()
  local file_path = vim.fn.expand("%:p")
  local project_path = vim.fn.getcwd()

  M.send(reload_project_command(project_path))
  send_file(file_path)
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
