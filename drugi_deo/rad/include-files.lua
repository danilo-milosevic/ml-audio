function Para(para)
  -- Reconstruct the full text from all inline elements
  local text = pandoc.utils.stringify(para)
  
  -- Match the include pattern
  local file = text:match("^{{%s*include%s+(.-)%s*}}$")
  
  if file then
    local f = io.open(file, 'r')
    if f then
      local content = f:read('*a')
      f:close()
      -- Parse the markdown content
      local doc = pandoc.read(content, 'markdown')
      -- Process the included document through the same filter (recursive)
      return pandoc.walk_block(pandoc.Div(doc.blocks), {Para = Para}).content
    else
      return pandoc.Para{pandoc.Str('[ERROR: Cannot read file: ' .. file .. ']')}
    end
  end
  
  return nil
end