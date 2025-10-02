# --- 使い方: ---
#   ./render_obj.sh [フレーム数]
#   （例）./render_obj.sh 33
#
# 引数が無い場合は既定値 33 フレームで実行します。
# --------------------------------------------

# フレーム数の取得
FRAMES=${1:-33}

# # XML 一覧
# xml_list=(
#   render_circle11.xml  render_circle21.xml  render_circle31.xml
#   render_circle22.xml  render_circle12.xml  render_circle13.xml

#   render_triangle11.xml  render_triangle21.xml  render_triangle31.xml
#   render_triangle22.xml  render_triangle12.xml  render_triangle13.xml

#   render_square11.xml  render_square21.xml  render_square31.xml
#   render_square22.xml  render_square12.xml  render_square13.xml

#   render_L11.xml  render_L21.xml  render_L31.xml
#   render_L22.xml  render_L12.xml  render_L13.xml

#   render_star11.xml  render_star21.xml  render_star31.xml
#   render_star22.xml  render_star12.xml  render_star13.xml

#   render_pentagon11.xml  render_pentagon21.xml  render_pentagon31.xml
#   render_pentagon22.xml  render_pentagon12.xml  render_pentagon13.xml
# )

xml_list=(
  render_circle11.xml
)

for xml in "${xml_list[@]}"; do
  echo "=== rendering $xml  ($FRAMES frames) ==="
  python ./grainRender.py "./png_input/${xml}" "${FRAMES}"
done