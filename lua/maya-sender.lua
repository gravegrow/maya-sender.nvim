local function setup(opts)
	opts = opts or {}

	for k, v in pairs(opts) do
		vim.g["MayaSender_" .. k] = v
	end
end

return { setup = setup }
