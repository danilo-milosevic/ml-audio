function Para(para)
  local text = pandoc.utils.stringify(para)
  local file = text:match("^{{%s*include%s+(.-)%s*}}$")
  
  if file then
    local f = io.open(file, 'r')
    if f then
      local content = f:read('*a')
      f:close()
      local doc = pandoc.read(content, 'markdown')
      return pandoc.walk_block(
              pandoc.Div(doc.blocks),
              {
                Para = Para,
                RawBlock = RawBlock
              }
            ).content
    else
      return pandoc.Para{pandoc.Str('[ERROR: Cannot read file: ' .. file .. ']')}
    end
  end
  
  return nil
end

function RawBlock(el)

  if FORMAT ~= "docx" then
    return nil
  end

  if el.format ~= "tex" and el.format ~= "latex" then
    return nil
  end

  local text = el.text

  if not text:match("\\begin%s*{figure}") then
    return nil
  end

  local path = text:match("\\includegraphics%s*%b[]%s*%{([^}]+)%}")
  if not path then
    path = text:match("\\includegraphics%s*%{([^}]+)%}")
  end

  local caption = text:match("\\caption%{(.-)%}")

  if not path then
    return nil
  end

  local caption_inlines = {}
  if caption then
    local parsed = pandoc.read(caption, "markdown")
    if parsed.blocks[1] and parsed.blocks[1].content then
      caption_inlines = parsed.blocks[1].content
    end
  end

  return pandoc.Para{
    pandoc.Image(caption_inlines, path)
  }
end