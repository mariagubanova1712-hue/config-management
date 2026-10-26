% menu: 1.0.0, 1.1.0, 1.2.0, 1.3.0, 1.4.0, 1.5.0
% dropdown: 1.8.0, 2.0.0, 2.1.0, 2.2.0, 2.3.0
% icons: 1.0.0, 2.0.0
enum MENU = {menu_1_0_0, menu_1_1_0, menu_1_2_0, menu_1_3_0, menu_1_4_0, menu_1_5_0};
enum DROPDOWN = {dropdown_1_8_0, dropdown_2_0_0, dropdown_2_1_0, dropdown_2_2_0, dropdown_2_3_0};
enum ICONS = {icons_1_0_0, icons_2_0_0};

var MENU: menu;
var DROPDOWN: dropdown;
var ICONS: icons;

% root 1.0.0 -> menu >=1.0.0, icons ^1.0.0
constraint icons = icons_1_0_0;
% menu 1.1.0..1.5.0 -> dropdown ^2.0.0
constraint menu >= menu_1_1_0 -> dropdown >= dropdown_2_0_0;
% menu 1.0.0 -> dropdown ^1.8.0
constraint menu = menu_1_0_0 -> dropdown = dropdown_1_8_0;
% dropdown 2.x -> icons ^2.0.0
constraint dropdown >= dropdown_2_0_0 -> icons = icons_2_0_0;

solve maximize menu;   % как менеджер пакетов: берём самую свежую подходящую версию
output ["root 1.0.0\n\(menu)\n\(dropdown)\n\(icons)\n"];
