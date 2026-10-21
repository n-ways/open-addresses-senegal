-- Filters for the PDF build. The markdown on the web stays plain.
-- 1. A figure uses its vector PDF in the paper; the web page uses the SVG.
function Image(img)
  img.src = img.src:gsub('%.svg$', '.pdf')
  return img
end

-- 2. Column widths follow the content: a table that fits the line is set at its
--    natural width; otherwise each column gets a share of the line in proportion to
--    its longest cell (code counted wider, at least its longest header word, capped
--    so that one long cell cannot starve the rest).
-- (paths are already raw \nolinkurl here: inline filters run before block filters)
local function cell_len(c)
  local code = false
  local div = pandoc.Div(c.contents):walk({
    Code = function() code = true end,
    RawInline = function(r)
      local path = r.text:match('^{\\urlstyle{tt}\\nolinkurl{(.*)}}$')
      if path then code = true; return pandoc.Str(path) end
    end})
  local n = utf8.len(pandoc.utils.stringify(div)) or 0
  return code and math.ceil(n * 1.5) or n, code
end

-- text may break at a hyphen, so its parts count as words (code breaks only at spaces)
local function longest_word(c, pattern)
  local m = 0
  for w in pandoc.utils.stringify(pandoc.Div(c.contents)):gmatch(pattern or '[^%s%-]+') do m = math.max(m, utf8.len(w) or #w) end
  return m
end

function Table(t)
  local n = #t.colspecs
  local body, head, headword, bodyword = {}, {}, {}, {}
  for i = 1, n do body[i], head[i], headword[i], bodyword[i] = 1, 1, 1, 1 end
  for _, row in ipairs(t.head.rows) do
    for i, c in ipairs(row.cells) do
      if i <= n then head[i] = math.max(head[i], (cell_len(c))); headword[i] = math.max(headword[i], longest_word(c)) end
    end
  end
  for _, b in ipairs(t.bodies) do
    for _, row in ipairs(b.body) do
      for i, c in ipairs(row.cells) do
        if i <= n then
          local len, code = cell_len(c)
          body[i] = math.max(body[i], len)
          -- code is set in a wider font and is not wrapped by word
          bodyword[i] = math.max(bodyword[i], code and math.ceil(1.5 * longest_word(c, '%S+')) or longest_word(c))
        end
      end
    end
  end
  local natural = 0
  for i = 1, n do natural = natural + math.max(body[i], head[i]) + 2 end
  if natural <= 95 then
    for i = 1, n do t.colspecs[i][2] = pandoc.ColWidthDefault end
  else
    local need, sum = {}, 0
    for i = 1, n do
      -- a cell of several words may wrap, but its longest word must fit with room to spare
      local wrap = math.max(16, math.ceil(1.2 * bodyword[i]))
      need[i] = math.min(math.max(math.min(body[i], wrap), bodyword[i] + 2, headword[i] + 1, 5), 40)
      sum = sum + need[i]
    end
    for i = 1, n do t.colspecs[i][2] = 0.98 * need[i] / sum end
  end
  -- a short table (up to about half a page) is never split across pages: it starts on the next page when the
  -- room left cannot hold it (each row as many lines as its longest cell wraps to in
  -- its column, plus the head, the caption and the rules)
  local function row_lines(cells)
    if natural <= 95 then return 1 end
    local m = 1
    for i, c in ipairs(cells) do
      if i <= n then m = math.max(m, math.ceil((cell_len(c)) / math.max(1, t.colspecs[i][2] * 100))) end
    end
    return m
  end
  local rows, lines = 0, 4
  for _, row in ipairs(t.head.rows) do lines = lines + row_lines(row.cells) end
  for _, b in ipairs(t.bodies) do
    for _, row in ipairs(b.body) do rows = rows + 1; lines = lines + row_lines(row.cells) end
  end
  local pre = nil
  if rows <= 15 and lines <= 28 then
    pre = pandoc.RawBlock('latex', '\\needspace{' .. lines .. '\\baselineskip}')
  end
  if n >= 9 then
    -- many columns: smaller type and narrower gutters leave the text columns room for their longest word
    local out = {pandoc.RawBlock('latex', '\\begingroup\\renewcommand{\\papertablesize}{\\footnotesize}\\setlength{\\tabcolsep}{3pt}'), t,
                 pandoc.RawBlock('latex', '\\endgroup')}
    if pre then table.insert(out, 1, pre) end
    return out
  end
  if pre then return {pre, t} end
  return t
end

-- 3. File paths and other code without spaces may break after a slash or a dot
--    (xurl), so that a long path never runs into the margin.
function Code(c)
  if c.text:match('^[%w%./_%-]+$') and c.text:match('[/]') then
    return pandoc.RawInline('latex', '{\\urlstyle{tt}\\nolinkurl{' .. c.text .. '}}')
  end
end

-- 4. Unnumbered sections (references, appendix) set the running head.
function Header(h)
  if h.level == 1 and h.classes:includes('unnumbered') then
    local title = pandoc.utils.stringify(h.content)
    local out = {h, pandoc.RawBlock('latex', '\\markboth{' .. title .. '}{}')}
    if title:match('^Appendix') or title:match('^Annexe') then
      table.insert(out, 1, pandoc.RawBlock('latex', '\\clearpage'))
    end
    return out
  end
end

-- 5. French typography puts a thin space before a colon. Identifiers such as
--    EPSG:31028 or ISO 19160-1:2015 keep theirs closed.
function Pandoc(doc)
  local lang = doc.meta.lang and pandoc.utils.stringify(doc.meta.lang) or ''
  if not lang:match('^fr') then return nil end
  return doc:walk({Str = function(s)
    if s.text:match('%w:%w') or s.text:match('^:%w') then
      return pandoc.RawInline('latex', '{\\NoAutoSpacing ' .. s.text:gsub('([#$%%&_{}])', '\\%1') .. '}')
    end
  end})
end
