# Xbox button guide generation

- Tool: built-in `image_gen.imagegen` (no CLI fallback).
- Purpose: Chinese default button guide for Vibe with Xbox.
- Sources: `vibe_with_xbox/config.py` (`DEFAULT_CONFIG`, `mapping_for_control`) and `vibe_with_xbox/bridge.py` (text input and RT hold handling).
- This is a static default-configuration guide, not a live connection or mapping status screen.

> **No button guide image is currently committed.** The two generated PNGs were removed because
> they showed the earlier mapping (Dictation on X, hold-Start pause, LB / RB switching panes),
> while the prompts below describe the current one (X holds the right Option modifier, Start
> types the restart instruction on a single press, LB / RB switch tmux sessions).
> Before regenerating, note that the layout spec has no right-stick card — the right stick
> switches tmux panes in the shipped default config, so a five-cards-per-side layout cannot
> show the full mapping.

## Initial prompt

Use case: infographic-diagram.
Asset type: A final, shareable Simplified Chinese button guide image for the real macOS product "Vibe with Xbox". This is an instruction graphic, not an interactive settings UI.
Primary request: Create a polished diagram in the style of a light macOS button-mapping guide: one large realistic Xbox wireless controller in the center, rounded explanatory cards on the left and right, thin curved leader lines connecting every mapped button to its correct card. The user's reference is a white remote-control mapping screen; borrow its clean central-product / two-side-callouts composition, but draw an Xbox controller and use ONLY the exact actual mappings below.
Canvas: landscape 4:3, target 2400 x 1800 pixels, high-resolution crisp Chinese typography, generous outer margins.
Visual design: warm white background, near-black text, pale neutral-gray cards with subtle borders, restrained Xbox green for the product accent, original green A/red B/blue X/yellow Y colors as small button badges; orange used only for the destructive RT hold warning. Quiet premium product documentation, lots of breathing room, consistent grid, thin smooth gray leader lines, absolutely no line through text. No watermark.
Header at top left, exact text: "Vibe with Xbox" and large bold Chinese title "手柄按键说明". Subtitle: "用 Xbox 手柄操作 Claude Code 与 tmux".
Top-right pill, exact text: "默认映射". Do not show a fake connection status, battery level, or switch.
Central subject: accurate matte charcoal-black Xbox Series wireless controller, front view with a slight elevated angle to clearly expose RB, LB, and the rear RT trigger. Correct asymmetric sticks: left stick on upper-left, D-pad lower-left, right stick lower-right. Correct face-button diamond: yellow Y at top, red B at right, green A at bottom, blue X at left. Xbox logo central upper, small Menu/Start button with three horizontal lines to right of center; never confuse with left View button or lower Share button. Large and well lit, substantial realistic body, soft contact shadow, no hands. Label real shoulder controls LB, RB, RT subtly on or next to their physical locations.
Composition: product occupies the middle 45% of canvas. Five orderly callout cards down each side, each about 23% width. The left final card is a neutral unmapped-controls note without a leader. Text is dark, legible, not tiny. Card headers bold, action lines slightly larger than helper descriptions. Small gray input-gesture pills say "单击", "拨动", or hold duration as specified. Do NOT add double-click columns, empty options, app-launch controls, or fictional customizable actions.

LEFT COLUMN, top to bottom, exact text in cards:
1. header "LB · 左肩键"; gesture "单击"; action "上一个会话"; helper "切换 tmux session". Leader connects exactly to left bumper LB.
2. header "左摇杆"; gesture "拨动"; two compact action cells "上推  ↑" and "下推  ↓"; helper "持续拨住可连续移动". Leader connects exactly to left analog stick.
3. header "十字方向键"; action "新建 tmux 窗格"; four small orderly cells "↑ 上方" / "↓ 下方" / "← 左侧" / "→ 右侧". Leader connects exactly to D-pad.
4. header "Start · 菜单键"; gesture "单击"; action "粘贴重启指令"; helper "不自动按 Enter". Leader connects to the small three-line Menu button right of center, NOT to the Xbox logo.
5. neutral note card, no leader, header "暂未映射"; text "LT、摇杆按下"; next text line "View、Share、Xbox 键"; final helper "左摇杆左右方向暂未映射".

RIGHT COLUMN, top to bottom, exact text in cards:
1. A taller two-row shoulder-control card with clear divider. First row: header "RB · 右肩键", gesture "单击", action "下一个会话". Separate leader to right bumper RB. Second row with pale orange highlight: header "RT · 右扳机", gesture "长按 0.7 秒", action "关闭当前 tmux 窗格". Separate leader to rear right trigger RT; NOT to RB. Tiny orange helper "注意：将终止该窗格".
2. Yellow Y badge header "Y 键"; gesture "单击"; action "↓ + Enter"; helper "下移一项并确认". Leader connects exactly to yellow Y, the top face button.
3. Blue X badge header "X 键"; gesture "按住"; action "右 Option"; helper "macOS 修饰键 · 松开即释放". Leader connects exactly to blue X, the left face button.
4. Red B badge header "B 键"; gesture "单击"; action "Esc"; helper "取消 / 返回". Leader connects exactly to red B, the right face button.
5. Green A badge header "A 键"; gesture "单击"; action "Enter"; helper "确认 / 提交". Leader connects exactly to green A, the bottom face button.

Footer: thin horizontal divider and a clean compact setup strip. Bold small heading "使用前". Three numbered items on one row or three balanced columns:
"01  连接 Xbox 手柄"
"02  授予 macOS 辅助功能权限"
"03  将焦点置于目标应用"
Under them, muted note exact text: "窗格操作需在 tmux 会话中使用 · 本图为默认配置，请以实际配置为准".
Critical invariants: Simplified Chinese must be correct and readable verbatim. RT is a hold, never single-click. Start types the configured restart instruction on a single press and never submits it. D-pad creates panes, never navigates prompts; left stick up/down navigates. Do not imply Y universally means yes. No claim that unmapped physical controls are disabled system-wide. All leader lines terminate at correct physical controls; route smoothly without crossings where possible.

## First correction

Use case: precise-object-edit.
Edit the attached Vibe with Xbox Chinese button guide. Preserve the layout, all Chinese text, realistic controller, card illustrations, typography, green branding, and footer. Correct ONLY these rendering/technical mistakes:
1. BACKGROUND: the image currently contains transparent/black noisy broken regions behind the header and footer. Restore a fully OPAQUE SOLID WHITE (#ffffff) canvas everywhere, with only the existing gentle gray controller shadow and clean pale cards. Remove ALL black/green/cyan speckle corruption, transparent pixels, cloudy blobs, and edge artifacts. The header and footer must be extremely legible on clean white. This is a complete finished white-background document, NOT a transparent cutout. The resulting PNG must visually have a continuous pure white background.
2. The PHYSICAL LEFT SHOULDER BUMPER on the large central controller incorrectly says "RB". It must say "LB", one clean label, matching the left LB card. Keep the physical right bumper labeled "RB". Keep RT on the right trigger.
3. Re-route right-side callout lines so every card matches its control. Use thin neutral-gray curved leaders, small green endpoint dots, no line through card text. Input image dimensions are 1448 x 1086; coordinates below identify approximate locations in the input, do not print coordinates. Right shoulder card has TWO distinct leaders: RB at central-controller coordinate (880,330) -> the RB row's left edge (1093,166); RT at (949,286) -> the RT row's left edge (1093,286). The RT leader MUST enter the RT ROW INSIDE THE TOP CARD, not the Y card.
Y yellow top face button at (936,448) -> Y card left edge at (1093,395). X blue left face button at (887,506) -> X card left edge at (1093,532). B red right face button at (982,511) -> B card left edge at (1093,665). A green bottom face button at (928,568) -> A card left edge at (1093,800). In particular Y must NOT connect to the X card. Each face button gets exactly ONE leader. Check the Y/X/B/A button colors and endpoints individually.
4. Restore any missing LEFT LB leader: left LB card edge (353,230) -> large controller LEFT shoulder bumper (522,332). Keep left-stick / D-pad / Start card leaders and their correct endpoints unchanged.
Use original 4:3 aspect ratio. Keep all exact wording and timings unchanged: RT 长按 0.7 秒; Start 长按 1 秒后松开. Keep the original short product usage footer. No new content, no watermark.


## Final correction

Edit this existing Chinese Xbox instruction graphic. Keep the controller, white background, title, layout, all left-column cards, shoulder cards, Y card, A card, and EVERY existing connector path exactly unchanged. This is a precise correction, not a redesign.

ONLY make these changes:
A. Correct the subtitle under the large title to this EXACT text:
"用 Xbox 手柄操作 Claude Code 与 tmux"
Do not write Cloud-Games or gaming language.

B. Swap the ENTIRE contents of the two middle right-side cards (the X card and B card), WITHOUT changing their connector paths. In the input, the physical red B button already connects to the upper of these two cards, and the physical blue X button already connects to the lower. The card contents must agree with these lines.
After editing, the right-side face-button card order from top to bottom MUST be Y, B, X, A.
The B card immediately below Y must have RED B badge, header "B 键", "单击" pill, large "Esc", helper "取消 / 返回", and RED B button thumbnail.
The X card immediately above A must have BLUE X badge, header "X 键", "按住" pill, large "右 Option", helper "macOS 修饰键 · 松开即释放", and BLUE X button thumbnail.
Keep the thin connector from the physical red B to the B card and from the physical blue X to the X card. No swapping of physical controller buttons. No change to any other button's connector.

C. Footer: preserve footer layout and green numbered circles, replace only text.
01 label exactly "连接 Xbox 手柄"
02 label exactly "授予 macOS 辅助功能权限"
03 label exactly "将焦点置于目标应用"
Replace the entire tiny final footer sentence with EXACTLY:
"窗格操作需在 tmux 会话中使用 · 本图为默认配置，请以实际配置为准"
No other footer sentence, no made-up instructions, no mention of games.

Keep every other detail and all other text unchanged. Keep opaque pure white canvas and the original 4:3 composition. Carefully spell all exact text.

## Final artifact and verification

- File: `docs/assets/xbox-button-guide-zh.png` — deleted; see the note at the top.
- When it was generated, it was verified against the layout of that time: all default control groups and their leader lines, including the right-side Y / B / X / A order, RT closing a pane after 0.7 seconds held, the subtitle, the tmux requirement, and the default-configuration disclaimer.
- It predated the Option-hold and Start-text changes, so it was never verified against the revised prompts above.

## English localization prompt

Use case: text-localization.
Asset type: English controller button guide for the open-source project "Vibe with Xbox".
Input image: the attached Chinese guide is the edit target.
Primary request: Translate and replace every Chinese text string in the image with the exact English copy below. Preserve the controller, button photos, button colors, connector endpoints, layout, white background, shadows, cards, typography hierarchy, green branding, orange RT warning, and 4:3 canvas. This is a localization edit, not a redesign.
Typography: crisp professional English sans serif, readable at README width. Resize English type within each existing card when needed, but never crop, truncate, overlap, or run text outside a card. Use all text verbatim and add no other wording.

Header:
Brand stays exactly "Vibe with Xbox"
Main title: "CONTROLLER BUTTON GUIDE"
Subtitle: "Control Claude Code and tmux with an Xbox controller"
Top-right pill: "DEFAULT MAPPING"

Left cards from top to bottom:
1. Header "LB · LEFT BUMPER"; gesture pill "PRESS"; action "PREVIOUS SESSION"; helper "Switch tmux session"
2. Header "LEFT STICK"; gesture pill "TILT"; two cells "UP  ↑" and "DOWN  ↓"; helper "Hold to repeat"
3. Header "D-PAD"; action "NEW TMUX PANE"; four cells "↑  ABOVE", "↓  BELOW", "←  LEFT", "→  RIGHT"
4. Header "START · MENU"; gesture pill "PRESS"; action "TYPE RESTART INSTRUCTION"; helper "Does not press Enter"
5. Header "UNMAPPED"; line 1 "LT and stick clicks"; line 2 "View, Share, Xbox button"; line 3 "Left/right left-stick input"

Right cards from top to bottom:
1. Keep the existing combined two-row shoulder card and divider.
   First row: header "RB · RIGHT BUMPER"; gesture pill "PRESS"; action "NEXT SESSION".
   Second row: header "RT · RIGHT TRIGGER"; orange gesture pill "HOLD 0.7S"; action "CLOSE CURRENT TMUX PANE"; orange helper "WARNING: TERMINATES PANE".
2. Yellow badge header "Y BUTTON"; gesture pill "PRESS"; action "↓ + Enter"; helper "Move down and confirm"
3. Red badge header "B BUTTON"; gesture pill "PRESS"; action "Esc"; helper "Cancel / Back"
4. Blue badge header "X BUTTON"; gesture pill "HOLD"; action "RIGHT OPTION"; helper "macOS modifier · releases with X"
5. Green badge header "A BUTTON"; gesture pill "PRESS"; action "Enter"; helper "Confirm / Submit"

Footer:
Heading "BEFORE USE"
Green step 01: "CONNECT XBOX CONTROLLER"
Green step 02: "GRANT macOS ACCESSIBILITY"
Green step 03: "FOCUS THE TARGET APP"
Centered bottom note: "Pane controls require a tmux session · Default mapping shown; custom configs may differ"

Critical invariants:
- Result is fully English: remove every Chinese character. Do not translate product names, button letters, Claude Code, macOS, or tmux.
- Keep every physical controller label and all connector paths unchanged. The large controller's left bumper is LB and right bumper is RB.
- Right face-button card order remains Y, B, X, A. Physical Y connects to Y; B to B; X to X; A to A.
- RT connects to the RT row inside the top combined card, not the Y card. RT is HOLD 0.7S, never press.
- Start says PRESS and types the restart instruction without pressing Enter.
- D-pad creates tmux panes; left stick navigates up/down.
- No fake battery, connection state, switch, watermark, QR code, URL, gaming language, or new controls.
- Keep a fully opaque solid white background with no transparent, black, green, or cyan artifacts.

## English artifact verification

- File: `docs/assets/xbox-button-guide-en.png` — deleted; see the note at the top.
- When it was generated, it was verified against the layout of that time: all visible copy is English, the subtitle and three setup steps are complete, the Y / B / X / A card order matches the controller leader lines, and the LB / RB / RT labels and RT 0.7-second hold are correct.
- It still showed the Dictation and hold-Start behaviour, so it was never verified against the revised prompts above.
