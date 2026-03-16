import os
from moviepy import ColorClip, TextClip, CompositeVideoClip
from django.conf import settings

def generate_video_preview(script_instance):
    """
    Генерирует простое видео на основе текста сценария.
    """
    try:
        # Убеждаемся, что MEDIA_ROOT существует
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # Настройки видео
        duration = 5
        size = (1080, 1920) # Формат Reels
        fps = 24
        
        # Создаем фоновый клип (темно-синий/черный)
        background = ColorClip(size=size, color=(13, 17, 23), duration=duration)
        
        # Создаем текстовый клип
        # Примечание: В реальном окружении Docker может потребоваться установка шрифтов
        text = TextClip(
            text=script_instance.script_text,
            font_size=50,
            color='white',
            method='caption',
            size=(size[0]*0.8, None)
        ).with_duration(duration).with_position('center')
        
        # Собираем финальное видео
        video = CompositeVideoClip([background, text])
        
        # Путь для сохранения
        filename = f"script_{script_instance.id}.mp4"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        # Рендеринг
        video.write_videofile(output_path, fps=fps, codec='libx264', audio=False)
        
        # Обновляем инстанс
        script_instance.video_file = f"videos/{filename}"
        script_instance.status = 'completed'
        script_instance.save()
        
        return True
    except Exception as e:
        print(f"Ошибка генерации видео: {e}")
        script_instance.status = 'failed'
        script_instance.save()
        return False
