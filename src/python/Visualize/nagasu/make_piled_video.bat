set ffmpeg_path=C:\Users\naoto\Downloads\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin\
set tameru_path=C:\Users\naoto\nagasu_render\png
set frame_rate=30

%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_circle11\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/circle11.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_circle21\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/circle21.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_circle31\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/circle31.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_circle22\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/circle22.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_circle12\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/circle12.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_circle13\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/circle13.mp4

%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_triangle11\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/triangle11.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_triangle21\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/triangle21.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_triangle31\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/triangle31.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_triangle22\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/triangle22.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_triangle12\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/triangle12.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_triangle13\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/triangle13.mp4

%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_square11\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/square11.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_square21\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/square21.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_square31\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/square31.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_square22\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/square22.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_square12\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/square12.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_square13\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/square13.mp4

%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_L11\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/L11.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_L21\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/L21.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_L31\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/L31.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_L22\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/L22.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_L12\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/L12.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_L13\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/L13.mp4

%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_pentagon11\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/pentagon11.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_pentagon21\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/pentagon21.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_pentagon31\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/pentagon31.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_pentagon22\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/pentagon22.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_pentagon12\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/pentagon12.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_pentagon13\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/pentagon13.mp4

%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_star11\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/star11.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_star21\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/star21.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_star31\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/star31.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_star22\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/star22.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_star12\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/star12.mp4
%ffmpeg_path%\ffmpeg.exe -i %tameru_path%\png_star13\%%d.png -vcodec libx264 -pix_fmt yuv420p -r %frame_rate% ./movie/star13.mp4

