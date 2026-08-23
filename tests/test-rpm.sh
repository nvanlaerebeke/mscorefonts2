#!/usr/bin/bash

set -euo pipefail

rpm_path="${1:-/tmp/package.rpm}"
package_name="msttcore-fonts-installer"
font_dir="/usr/share/fonts/msttcore"
installer="/usr/lib/msttcore-fonts-installer/refresh-msttcore-fonts.sh"
installed_list="/usr/lib/msttcore-fonts-installer/installed-list.txt"

fail() {
    echo "TEST FAILED: $*" >&2
    exit 1
}

test -f "$rpm_path" || fail "mounted RPM not found at $rpm_path"

echo "Installing $rpm_path on Fedora 43"
dnf -y install "$rpm_path"

rpm -q "$package_name" >/dev/null || fail "$package_name is not installed"

grep -Fx 'mirror=https://downloads.sourceforge.net/corefonts' "$installer" >/dev/null \
    || fail "corefonts HTTPS mirror is not configured"
grep -Fx 'mirror_update=https://downloads.sourceforge.net/mscorefonts2' "$installer" >/dev/null \
    || fail "mscorefonts2 HTTPS mirror is not configured"
if grep -Eq '^mirror(_update)?=http://' "$installer"; then
    fail "installer still contains a plain-HTTP mirror"
fi

mapfile -t expected_font_paths < <(
    rpm -ql "$package_name" | grep -E "^${font_dir}/.*\\.ttf$"
)
expected_fonts="${#expected_font_paths[@]}"
installed_fonts="$(find "$font_dir" -maxdepth 1 -type f -name '*.ttf' -size +1024c \
    | wc -l)"

test "$expected_fonts" -gt 0 || fail "RPM does not track any expected fonts"
for font_path in "${expected_font_paths[@]}"; do
    test -f "$font_path" || fail "expected font is missing: $font_path"
    test -n "$(find "$font_path" -type f -size +1024c -print -quit)" \
        || fail "font placeholder was not replaced: $font_path"
done

test "$installed_fonts" -ge "$expected_fonts" \
    || fail "expected at least $expected_fonts installed fonts, found $installed_fonts"

test -s "$font_dir/fonts.dir" || fail "fonts.dir was not generated"
test -s "$font_dir/fonts.scale" || fail "fonts.scale was not generated"
grep -E '^[^[:space:]]+\.ttf[[:space:]]' "$font_dir/fonts.dir" >/dev/null \
    || fail "fonts.dir does not contain a generated font index"
grep -E '^[^[:space:]]+\.ttf[[:space:]]' "$font_dir/fonts.scale" >/dev/null \
    || fail "fonts.scale does not contain a generated font index"
test -s "$installed_list" || fail "downloaded-file manifest was not generated"

fc-list | grep -F "$font_dir/" >/dev/null \
    || fail "fontconfig does not list the installed fonts"

echo "PASS: installed $installed_fonts fonts and registered them with fontconfig"
