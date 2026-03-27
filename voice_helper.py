"""
Голосовые команды - распознавание и синтез речи
Использует Vosk (STT) и gTTS (TTS) - полностью бесплатно
"""
import os
import json
import logging
import shutil
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)

# Находим ffmpeg и ffprobe при загрузке модуля
_ffmpeg_path = None
_ffprobe_path = None

def _find_ffmpeg():
    """Найти ffmpeg и ffprobe при загрузке модуля"""
    global _ffmpeg_path, _ffprobe_path
    
    # Сначала проверяем стандартные пути напрямую (самый надежный способ)
    standard_paths_ffmpeg = [
        '/usr/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
        '/opt/ffmpeg/bin/ffmpeg',
        '/bin/ffmpeg',
    ]
    
    standard_paths_ffprobe = [
        '/usr/bin/ffprobe',
        '/usr/local/bin/ffprobe',
        '/opt/ffmpeg/bin/ffprobe',
        '/bin/ffprobe',
    ]
    
    # Ищем ffmpeg
    for path in standard_paths_ffmpeg:
        if os.path.exists(path):
            try:
                if os.access(path, os.X_OK):
                    _ffmpeg_path = path
                    logger.info(f"Найден ffmpeg при загрузке: {path}")
                    break
            except:
                pass
    
    # Ищем ffprobe
    for path in standard_paths_ffprobe:
        if os.path.exists(path):
            try:
                if os.access(path, os.X_OK):
                    _ffprobe_path = path
                    logger.info(f"Найден ffprobe при загрузке: {path}")
                    break
            except:
                pass
    
    # Если не нашли через стандартные пути, пробуем через which
    if not _ffmpeg_path:
        try:
            path = shutil.which('ffmpeg')
            if path and os.path.exists(path):
                _ffmpeg_path = path
                logger.info(f"Найден ffmpeg через which: {path}")
        except:
            pass
    
    if not _ffprobe_path:
        try:
            path = shutil.which('ffprobe')
            if path and os.path.exists(path):
                _ffprobe_path = path
                logger.info(f"Найден ffprobe через which: {path}")
        except:
            pass
    
    # Если ffprobe не найден, но ffmpeg есть, пробуем рядом
    if not _ffprobe_path and _ffmpeg_path:
        ffprobe_candidate = _ffmpeg_path.replace('ffmpeg', 'ffprobe')
        if os.path.exists(ffprobe_candidate):
            _ffprobe_path = ffprobe_candidate
            logger.info(f"Найден ffprobe рядом с ffmpeg: {ffprobe_candidate}")
    
    # Финальная проверка
    if _ffmpeg_path:
        logger.info(f"✅ ffmpeg найден: {_ffmpeg_path}")
    else:
        logger.warning("⚠️  ffmpeg не найден при загрузке модуля")
    
    if _ffprobe_path:
        logger.info(f"✅ ffprobe найден: {_ffprobe_path}")
    else:
        logger.warning("⚠️  ffprobe не найден при загрузке модуля")

# Ищем ffmpeg при загрузке модуля
_find_ffmpeg()

class VoiceHelper:
    """Класс для работы с голосовыми командами"""
    
    def __init__(self):
        self.vosk_model = None
        self.vosk_recognizer = None
        self.model_loaded = False
        self.model_error = None
        
        # Пытаемся загрузить Vosk модель
        self._load_vosk_model()
    
    def _load_vosk_model(self):
        """Загрузить модель Vosk для распознавания речи"""
        try:
            import vosk
            
            # Пробуем несколько возможных путей к модели
            base_dir = os.path.dirname(__file__)
            possible_paths = [
                os.path.join(base_dir, "vosk_models", "vosk-model-small-ru-0.22"),
                os.path.join(base_dir, "vosk_models", "vosk-model-ru-0.42"),
                os.path.join(os.getcwd(), "vosk_models", "vosk-model-small-ru-0.22"),
                os.path.join(os.getcwd(), "vosk_models", "vosk-model-ru-0.42"),
                "/opt/bot/vosk_models/vosk-model-small-ru-0.22",
                "/opt/bot/vosk_models/vosk-model-ru-0.42",
            ]
            
            # Также ищем любую модель в папке vosk_models
            vosk_dirs = [
                os.path.join(base_dir, "vosk_models"),
                os.path.join(os.getcwd(), "vosk_models"),
                "/opt/bot/vosk_models",
            ]
            
            model_path = None
            for path in possible_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    # Проверяем, что это действительно модель (есть папка am/ или graph/)
                    if os.path.exists(os.path.join(path, "am")) or os.path.exists(os.path.join(path, "graph")):
                        model_path = path
                        logger.info(f"Найдена модель Vosk: {model_path}")
                        break
            
            # Если не нашли по точным путям, ищем любую модель в папке
            if not model_path:
                for vosk_dir in vosk_dirs:
                    if os.path.exists(vosk_dir):
                        logger.info(f"Проверяю папку: {vosk_dir}")
                        try:
                            items = os.listdir(vosk_dir)
                            logger.info(f"Содержимое папки: {items}")
                            for item in items:
                                item_path = os.path.join(vosk_dir, item)
                                if os.path.isdir(item_path):
                                    logger.info(f"Проверяю папку: {item_path}")
                                    # Проверяем, что это модель (разные варианты структуры)
                                    has_am = os.path.exists(os.path.join(item_path, "am"))
                                    has_graph = os.path.exists(os.path.join(item_path, "graph"))
                                    has_conf = os.path.exists(os.path.join(item_path, "conf"))
                                    has_ivector = os.path.exists(os.path.join(item_path, "ivector"))
                                    
                                    # Модель должна иметь хотя бы одну из этих папок
                                    if has_am or has_graph or has_conf or has_ivector:
                                        model_path = item_path
                                        logger.info(f"✅ Найдена модель Vosk: {model_path}")
                                        logger.info(f"   Структура: am={has_am}, graph={has_graph}, conf={has_conf}, ivector={has_ivector}")
                                        break
                        except PermissionError:
                            logger.warning(f"Нет доступа к папке: {vosk_dir}")
                        except Exception as e:
                            logger.warning(f"Ошибка при проверке {vosk_dir}: {e}")
                        if model_path:
                            break
            
            # Если модели нет
            if not model_path:
                logger.warning("Vosk модель не найдена.")
                logger.info("Проверенные папки:")
                for vosk_dir in vosk_dirs:
                    if os.path.exists(vosk_dir):
                        logger.info(f"  - {vosk_dir}: существует")
                        try:
                            items = os.listdir(vosk_dir)
                            logger.info(f"    Содержимое: {items}")
                            for item in items:
                                item_path = os.path.join(vosk_dir, item)
                                if os.path.isdir(item_path):
                                    subitems = os.listdir(item_path)
                                    logger.info(f"    {item}/ содержит: {subitems[:5]}...")  # Первые 5 элементов
                        except Exception as e:
                            logger.warning(f"    Ошибка чтения: {e}")
                    else:
                        logger.info(f"  - {vosk_dir}: не существует")
                
                logger.info("\nДля работы голосовых команд:")
                logger.info("1. Убедитесь, что модель распакована правильно")
                logger.info("2. Структура должна быть: vosk_models/название-модели/am/ или graph/")
                logger.info("3. Скачайте модель: https://alphacephei.com/vosk/models")
                self.model_loaded = False
                self.model_error = "Модель не найдена. Проверьте структуру папки vosk_models/"
                return
            
            # Загружаем модель
            if not self.model_loaded:
                logger.info(f"Загрузка Vosk модели из {model_path}...")
                self.vosk_model = vosk.Model(model_path)
                self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
                self.model_loaded = True
                logger.info("✅ Vosk модель загружена успешно!")
                self.model_error = None
                
        except ImportError:
            logger.warning("Vosk не установлен. Установите: pip install vosk")
            self.model_loaded = False
            self.model_error = "Vosk не установлен. Выполните: pip install vosk"
        except Exception as e:
            logger.error(f"Ошибка загрузки Vosk модели: {e}")
            self.model_loaded = False
            self.model_error = f"Ошибка загрузки модели: {str(e)}"
    
    def speech_to_text(self, audio_data: bytes, audio_format: str = "ogg") -> Optional[str]:
        """
        Распознать речь из аудио
        
        Args:
            audio_data: Байты аудио файла
            audio_format: Формат аудио (ogg, wav, mp3)
            
        Returns:
            Распознанный текст или None
        """
        try:
            logger.info(f"Начинаю распознавание: формат={audio_format}, размер={len(audio_data)} байт")
            
            # Проверяем, загружена ли модель
            if not self.model_loaded:
                logger.error("Vosk модель не загружена!")
                return None
            
            if not self.vosk_model:
                logger.error("Vosk модель отсутствует!")
                return None
            
            logger.info("✅ Vosk модель загружена, начинаю конвертацию аудио...")
            
            # Конвертируем аудио в нужный формат
            wav_data = self._convert_to_wav(audio_data, audio_format)
            
            if not wav_data:
                logger.error("Не удалось конвертировать аудио в WAV")
                return None
            
            logger.info(f"✅ Аудио конвертировано в WAV: {len(wav_data)} байт")
            
            # Если Vosk модель загружена, используем её
            if self.model_loaded and self.vosk_model:
                logger.info("Начинаю распознавание с помощью Vosk...")
                result = self._recognize_with_vosk(wav_data)
                if result:
                    logger.info(f"✅ Распознано успешно: {result}")
                else:
                    logger.warning("⚠️ Vosk вернул пустой результат")
                return result
            else:
                # Fallback: используем онлайн распознавание (если доступно)
                logger.warning("Vosk модель не загружена, используем fallback")
                return self._recognize_fallback(audio_data)
                
        except Exception as e:
            logger.error(f"Ошибка распознавания речи: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _convert_to_wav(self, audio_data: bytes, audio_format: str) -> Optional[bytes]:
        """Конвертировать аудио в WAV формат для Vosk"""
        try:
            global _ffmpeg_path, _ffprobe_path
            
            # Используем найденные пути (найдены при загрузке модуля)
            ffmpeg_path = _ffmpeg_path
            ffprobe_path = _ffprobe_path
            
            # Если не найдены, пробуем найти еще раз (более тщательный поиск)
            if not ffmpeg_path:
                logger.warning("ffmpeg не найден при загрузке, пробую найти снова...")
                # Проверяем стандартные пути напрямую
                for candidate in ['/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg', '/bin/ffmpeg']:
                    if os.path.exists(candidate):
                        ffmpeg_path = candidate
                        _ffmpeg_path = candidate
                        logger.info(f"✅ Найден ffmpeg: {ffmpeg_path}")
                        break
                
                # Если не нашли, пробуем through which
                if not ffmpeg_path:
                    candidate = shutil.which('ffmpeg')
                    if candidate and os.path.exists(candidate):
                        ffmpeg_path = candidate
                        _ffmpeg_path = candidate
                        logger.info(f"✅ Найден ffmpeg через which: {ffmpeg_path}")
            
            if not ffprobe_path:
                logger.warning("ffprobe не найден при загрузке, пробую найти снова...")
                # Проверяем стандартные пути напрямую
                for candidate in ['/usr/bin/ffprobe', '/usr/local/bin/ffprobe', '/bin/ffprobe']:
                    if os.path.exists(candidate):
                        ffprobe_path = candidate
                        _ffprobe_path = candidate
                        logger.info(f"✅ Найден ffprobe: {ffprobe_path}")
                        break
                
                # Если не нашли, пробуем через which
                if not ffprobe_path:
                    candidate = shutil.which('ffprobe')
                    if candidate and os.path.exists(candidate):
                        ffprobe_path = candidate
                        _ffprobe_path = candidate
                        logger.info(f"✅ Найден ffprobe через which: {ffprobe_path}")
                
                # Если все еще не нашли, но ffmpeg есть, пробуем рядом
                if not ffprobe_path and ffmpeg_path:
                    candidate = ffmpeg_path.replace('ffmpeg', 'ffprobe')
                    if os.path.exists(candidate):
                        ffprobe_path = candidate
                        _ffprobe_path = candidate
                        logger.info(f"✅ Найден ffprobe рядом с ffmpeg: {ffprobe_path}")
            
            # Проверяем, что хотя бы ffmpeg найден
            if not ffmpeg_path or not os.path.exists(ffmpeg_path):
                logger.error("❌ ffmpeg не найден! Установите: sudo apt install ffmpeg")
                logger.error(f"   Проверенные пути: /usr/bin/ffmpeg, /usr/local/bin/ffmpeg, /bin/ffmpeg")
                logger.error(f"   Выполните на сервере: ls -la /usr/bin/ffmpeg")
                raise FileNotFoundError("ffmpeg not found")
            
            logger.info(f"✅ Использую ffmpeg: {ffmpeg_path}")
            if ffprobe_path:
                logger.info(f"✅ Использую ffprobe: {ffprobe_path}")
            
            # Импортируем AudioSegment и устанавливаем пути ДО использования
            from pydub import AudioSegment
            
            # Устанавливаем пути для pydub ПЕРЕД любым использованием
            AudioSegment.converter = ffmpeg_path
            logger.info(f"✅ Установлен converter: {ffmpeg_path}")
            
            if ffprobe_path and os.path.exists(ffprobe_path):
                AudioSegment.ffprobe = ffprobe_path
                logger.info(f"✅ Установлен ffprobe: {ffprobe_path}")
            else:
                # Если ffprobe не найден, используем ffmpeg
                AudioSegment.ffprobe = ffmpeg_path
                logger.warning(f"⚠️  ffprobe не найден, использую ffmpeg: {ffmpeg_path}")
            
            # Дополнительная проверка - убеждаемся что пути установлены
            actual_converter = getattr(AudioSegment, 'converter', None)
            actual_ffprobe = getattr(AudioSegment, 'ffprobe', None)
            logger.info(f"Проверка: AudioSegment.converter = {actual_converter}")
            logger.info(f"Проверка: AudioSegment.ffprobe = {actual_ffprobe}")
            
            # Создаем AudioSegment из байтов
            logger.info(f"Пробую конвертировать {audio_format} в WAV...")
            try:
                if audio_format == "ogg":
                    audio = AudioSegment.from_ogg(BytesIO(audio_data))
                elif audio_format == "mp3":
                    audio = AudioSegment.from_mp3(BytesIO(audio_data))
                elif audio_format == "wav":
                    return audio_data  # Уже WAV
                else:
                    audio = AudioSegment.from_file(BytesIO(audio_data), format=audio_format)
            except Exception as e:
                error_msg = str(e)
                if "ffprobe" in error_msg or "ffmpeg" in error_msg or "No such file" in error_msg:
                    logger.error(f"❌ pydub не может найти ffmpeg/ffprobe: {error_msg}")
                    logger.error("Пробую альтернативный способ конвертации через subprocess...")
                    # Альтернативный способ через subprocess
                    return self._convert_with_subprocess(audio_data, audio_format, ffmpeg_path)
                else:
                    raise
            
            # Конвертируем в моно, 16kHz (требования Vosk)
            audio = audio.set_channels(1)  # Моно
            audio = audio.set_frame_rate(16000)  # 16kHz
            
            # Нормализуем громкость (важно для распознавания)
            # Увеличиваем громкость если слишком тихо
            if audio.max_possible_amplitude > 0:
                max_db = audio.max_dBFS
                logger.info(f"Громкость аудио: {max_db:.1f} dB")
                
                # Нормализуем до -3 dB (почти максимум, но без клиппинга)
                target_db = -3.0
                
                if max_db < target_db:
                    gain_needed = target_db - max_db
                    # Ограничиваем усиление максимум до 20 dB
                    gain_needed = min(gain_needed, 20.0)
                    audio = audio.apply_gain(gain_needed)
                    logger.info(f"✅ Увеличена громкость на {gain_needed:.1f} dB (было {max_db:.1f} dB, стало {audio.max_dBFS:.1f} dB)")
                elif max_db > 0:
                    # Если слишком громко, уменьшаем
                    gain_needed = target_db - max_db
                    audio = audio.apply_gain(gain_needed)
                    logger.info(f"✅ Уменьшена громкость на {abs(gain_needed):.1f} dB (было {max_db:.1f} dB, стало {audio.max_dBFS:.1f} dB)")
                else:
                    logger.info(f"✅ Громкость в норме: {max_db:.1f} dB")
            
            # Экспортируем в WAV
            wav_buffer = BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            
            wav_data = wav_buffer.read()
            
            logger.info(f"Конвертировано: {len(wav_data)} байт, {audio.duration_seconds:.2f} сек, {audio.frame_rate}Hz, {audio.channels} канал")
            
            # Проверяем минимальную длину
            if audio.duration_seconds < 0.3:
                logger.warning(f"⚠️ Аудио очень короткое: {audio.duration_seconds:.2f} сек (рекомендуется минимум 1 сек)")
            
            # Сохраняем WAV для отладки (если включено)
            debug_enabled = os.getenv("VOICE_DEBUG", "false").lower() == "true"
            if debug_enabled:
                import time
                debug_dir = "debug_audio"
                if not os.path.exists(debug_dir):
                    os.makedirs(debug_dir)
                debug_path = os.path.join(debug_dir, f"audio_{int(time.time())}.wav")
                with open(debug_path, "wb") as f:
                    f.write(wav_data)
                logger.info(f"💾 Сохранено для отладки: {debug_path}")
            
            return wav_data
            
        except ImportError:
            logger.error("pydub не установлен. Установите: pip install pydub")
            return None
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Ошибка конвертации аудио: {error_msg}")
            
            if "ffprobe" in error_msg or "ffmpeg" in error_msg or "No such file" in error_msg:
                logger.error("")
                logger.error("=" * 60)
                logger.error("ПРОБЛЕМА С FFMPEG/FFPROBE")
                logger.error("=" * 60)
                logger.error(f"Ошибка: {error_msg}")
                logger.error("")
                logger.error("Проверьте на сервере:")
                logger.error("  1. ls -la /usr/bin/ffmpeg")
                logger.error("  2. ls -la /usr/bin/ffprobe")
                logger.error("  3. which ffmpeg")
                logger.error("  4. which ffprobe")
                logger.error("")
                logger.error("Если файлы не существуют, установите:")
                logger.error("  sudo apt update && sudo apt install -y ffmpeg")
                logger.error("=" * 60)
            else:
                logger.error(f"Другая ошибка конвертации: {e}")
                import traceback
                traceback.print_exc()
            return None
    
    def _convert_with_subprocess(self, audio_data: bytes, audio_format: str, ffmpeg_path: str) -> Optional[bytes]:
        """Альтернативный способ конвертации через subprocess"""
        try:
            import subprocess
            import tempfile
            
            logger.info("Использую subprocess для конвертации...")
            
            # Создаем временные файлы
            with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                output_path = output_file.name
            
            try:
                # Конвертируем через ffmpeg
                cmd = [
                    ffmpeg_path,
                    '-i', input_path,
                    '-ar', '16000',  # Частота дискретизации
                    '-ac', '1',      # Моно
                    '-f', 'wav',
                    '-y',            # Перезаписать выходной файл
                    output_path
                ]
                
                logger.info(f"Выполняю команду: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    logger.error(f"Ошибка ffmpeg: {result.stderr}")
                    return None
                
                # Читаем результат
                with open(output_path, 'rb') as f:
                    wav_data = f.read()
                
                logger.info(f"✅ Конвертировано через subprocess: {len(wav_data)} байт")
                return wav_data
                
            finally:
                # Удаляем временные файлы
                try:
                    os.unlink(input_path)
                    os.unlink(output_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Ошибка конвертации через subprocess: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _recognize_with_vosk(self, wav_data: bytes) -> Optional[str]:
        """Распознать речь с помощью Vosk"""
        try:
            import vosk
            import wave
            import struct
            
            if not self.vosk_model:
                logger.error("Vosk модель не загружена")
                return None
            
            # Создаем новый распознаватель для каждого аудио
            recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
            recognizer.SetWords(True)  # Включаем распознавание слов
            
            # Используем wave для правильного извлечения PCM данных
            wav_io = BytesIO(wav_data)
            
            try:
                with wave.open(wav_io, 'rb') as wf:
                    # Проверяем параметры аудио
                    sample_rate = wf.getframerate()
                    channels = wf.getnchannels()
                    sample_width = wf.getsampwidth()
                    
                    logger.info(f"WAV параметры: {sample_rate}Hz, {channels} канал(ов), {sample_width} байт/сэмпл")
                    
                    # Vosk требует 16kHz моно
                    if sample_rate != 16000:
                        logger.warning(f"Частота дискретизации {sample_rate}Hz, требуется 16000Hz")
                    
                    if channels != 1:
                        logger.warning(f"Каналов: {channels}, требуется моно (1 канал)")
                    
                    # Читаем все кадры
                    frames = wf.readframes(wf.getnframes())
                    
                    if len(frames) < 2000:  # Минимум ~0.06 сек при 16kHz
                        logger.error(f"Аудио слишком короткое: {len(frames)} байт")
                        return None
                    
                    logger.info(f"Прочитано {len(frames)} байт PCM данных ({len(frames) / 32000:.2f} сек)")
                    
            except Exception as e:
                logger.error(f"Ошибка чтения WAV: {e}")
                # Fallback: пробуем извлечь PCM вручную
                logger.info("Пробую извлечь PCM вручную...")
                
                # Ищем "data" чанк
                data_pos = wav_data.find(b'data')
                if data_pos == -1:
                    logger.error("Не найден 'data' чанк в WAV файле")
                    return None
                
                # Размер данных находится на позиции data_pos + 4 (4 байта)
                data_size = struct.unpack('<I', wav_data[data_pos + 4:data_pos + 8])[0]
                pcm_start = data_pos + 8
                frames = wav_data[pcm_start:pcm_start + data_size]
                
                logger.info(f"Извлечено {len(frames)} байт PCM данных (вручную)")
            
            # Обрабатываем PCM данные по частям
            # Важно: размер чанка должен быть кратным размеру сэмпла
            # При 16kHz, 16-bit mono: 1 секунда = 32000 байт
            # Vosk рекомендует чанки по 4000 байт (0.125 сек)
            chunk_size = 4000  # 0.125 секунды при 16kHz, 16-bit mono
            text_parts = []
            
            total_chunks = (len(frames) + chunk_size - 1) // chunk_size
            logger.info(f"Обработка {total_chunks} чанков PCM данных (размер чанка: {chunk_size} байт, всего PCM: {len(frames)} байт)...")
            
            processed_chunks = 0
            has_partial = False
            last_partial = ""
            
            # Обрабатываем все чанки
            for i in range(0, len(frames), chunk_size):
                chunk = frames[i:i + chunk_size]
                
                # Дополняем последний чанк до минимального размера если нужно
                if len(chunk) < chunk_size and i + chunk_size > len(frames):
                    # Последний чанк - дополняем нулями или оставляем как есть
                    pass
                
                if len(chunk) < 100:  # Слишком маленький чанк - пропускаем
                    break
                
                # Отправляем PCM чанк в распознаватель
                try:
                    accepted = recognizer.AcceptWaveform(chunk)
                    
                    if accepted:
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            text_parts.append(text)
                            logger.info(f"✅ Распознан фрагмент {processed_chunks + 1}: '{text}'")
                            has_partial = False  # Сброс, так как получили финальный результат
                except Exception as e:
                    logger.warning(f"Ошибка при обработке чанка {processed_chunks + 1}: {e}")
                
                processed_chunks += 1
                
                # Проверяем частичный результат каждые 3 чанка
                if processed_chunks % 3 == 0:
                    try:
                        partial = json.loads(recognizer.PartialResult())
                        partial_text = partial.get("partial", "").strip()
                        if partial_text and partial_text != last_partial:
                            has_partial = True
                            last_partial = partial_text
                            logger.info(f"📝 Частично ({processed_chunks}/{total_chunks}): '{partial_text}'")
                    except Exception as e:
                        logger.debug(f"Ошибка получения частичного результата: {e}")
            
            # Получаем финальный результат
            try:
                final_result = json.loads(recognizer.FinalResult())
                final_text = final_result.get("text", "").strip()
                
                logger.info(f"Финальный результат Vosk: '{final_text}'")
                logger.debug(f"Полный JSON результат: {final_result}")
                
                if final_text:
                    text_parts.append(final_text)
                    logger.info(f"✅ Финальный фрагмент: '{final_text}'")
            except Exception as e:
                logger.warning(f"Ошибка получения финального результата: {e}")
                final_text = ""
            
            # Объединяем все части
            recognized_text = " ".join(text_parts).strip()
            
            if recognized_text:
                logger.info(f"✅ ИТОГОВЫЙ РЕЗУЛЬТАТ: '{recognized_text}'")
                return recognized_text
            
            # Если нет финального результата, пробуем частичный
            logger.warning("⚠️ Vosk не распознал текст (пустой результат)")
            
            # Пробуем получить частичный результат
            try:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                logger.info(f"Последний частичный результат: '{partial_text}'")
                
                if partial_text and len(partial_text) > 1:  # Минимум 2 символа
                    logger.info(f"✅ Возвращаю частичный результат: '{partial_text}'")
                    return partial_text
            except Exception as e:
                logger.debug(f"Не удалось получить частичный результат: {e}")
            
            # Пробуем получить альтернативные результаты из финального
            try:
                final_result = json.loads(recognizer.FinalResult())
                logger.debug(f"Полный результат Vosk: {final_result}")
                
                # Проверяем разные поля
                if "text" in final_result and final_result["text"]:
                    alt_text = final_result["text"].strip()
                    if alt_text:
                        logger.info(f"✅ Альтернативный результат (text): '{alt_text}'")
                        return alt_text
                
                if "alternatives" in final_result:
                    for alt in final_result["alternatives"]:
                        alt_text = alt.get("text", "").strip()
                        if alt_text:
                            logger.info(f"✅ Альтернативный результат: '{alt_text}'")
                            return alt_text
            except Exception as e:
                logger.debug(f"Ошибка получения альтернатив: {e}")
            
            # Если есть частичный результат из цикла
            if last_partial and len(last_partial) > 1:
                logger.info(f"✅ Возвращаю последний частичный результат: '{last_partial}'")
                return last_partial
            
            logger.warning("❌ Не удалось распознать речь. Возможные причины:")
            logger.warning(f"  - Обработано чанков: {processed_chunks}/{total_chunks}")
            logger.warning(f"  - Размер PCM данных: {len(frames)} байт ({len(frames) / 32000:.2f} сек)")
            
            # Дополнительная диагностика
            try:
                # Пробуем получить последний частичный результат для диагностики
                partial = json.loads(recognizer.PartialResult())
                logger.warning(f"  - Последний частичный результат: '{partial}'")
            except:
                logger.warning("  - Частичных результатов нет")
            
            # Проверяем, есть ли вообще данные
            if len(frames) < 1000:
                logger.error(f"  ❌ Слишком мало PCM данных: {len(frames)} байт")
            elif len(frames) < 10000:
                logger.warning(f"  ⚠️  Мало PCM данных: {len(frames)} байт ({len(frames) / 32000:.2f} сек)")
            
            logger.warning("  Возможные причины:")
            logger.warning("  - Аудио слишком тихое")
            logger.warning("  - Аудио слишком короткое")
            logger.warning("  - Фоновый шум")
            logger.warning("  - Нечеткая речь")
            logger.warning("  - Модель не подходит для этого типа речи")
            logger.warning("  - Проблема с конвертацией аудио")
            
            # Сохраняем диагностическую информацию
            debug_enabled = os.getenv("VOICE_DEBUG", "false").lower() == "true"
            if debug_enabled:
                logger.warning(f"  💡 Включи VOICE_DEBUG=true для сохранения WAV файлов")
            
            return None
                
        except Exception as e:
            logger.error(f"Ошибка Vosk распознавания: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _recognize_fallback(self, audio_data: bytes) -> Optional[str]:
        """Fallback метод распознавания"""
        # Можно добавить онлайн API (например, Google Speech-to-Text или OpenAI Whisper)
        # Пока возвращаем None - нужна модель Vosk для работы
        logger.warning("Fallback распознавание не реализовано. Установите Vosk модель для офлайн режима.")
        logger.info("Скачайте модель: https://alphacephei.com/vosk/models")
        return None
    
    def get_setup_instructions(self) -> str:
        """Получить инструкции по настройке"""
        if self.model_error:
            return self.model_error
        
        if not self.model_loaded:
            return (
                "📥 **Установка Vosk модели:**\n\n"
                "1. Создайте папку:\n"
                "   `mkdir -p vosk_models`\n\n"
                "2. Скачайте модель (50 MB):\n"
                "   https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip\n\n"
                "3. Распакуйте в папку `vosk_models/`\n\n"
                "4. Перезапустите бота\n\n"
                "💡 Или используйте большую модель (1.5 GB) для лучшего качества"
            )
        
        return "✅ Vosk модель загружена и готова к работе!"
    
    def text_to_speech(self, text: str, language: str = "ru") -> Optional[BytesIO]:
        """
        Синтезировать речь из текста
        
        Args:
            text: Текст для синтеза
            language: Язык (ru, en, etc.)
            
        Returns:
            BytesIO с аудио файлом в формате OGG (для Telegram) или None
        """
        try:
            from gtts import gTTS
            from pydub import AudioSegment
            import tempfile
            
            # Создаем временный файл для MP3
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_mp3:
                tmp_mp3_path = tmp_mp3.name
            
            # Синтезируем речь в MP3
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(tmp_mp3_path)
            
            # Конвертируем MP3 в OGG (Telegram предпочитает OGG)
            try:
                audio = AudioSegment.from_mp3(tmp_mp3_path)
                
                # Создаем временный файл для OGG
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as tmp_ogg:
                    tmp_ogg_path = tmp_ogg.name
                
                # Экспортируем в OGG
                audio.export(tmp_ogg_path, format="ogg", codec="libopus")
                
                # Читаем OGG файл
                with open(tmp_ogg_path, 'rb') as f:
                    audio_data = f.read()
                
                # Удаляем временные файлы
                os.unlink(tmp_mp3_path)
                os.unlink(tmp_ogg_path)
                
            except Exception as e:
                # Если конвертация не удалась, используем MP3
                logger.warning(f"Не удалось конвертировать в OGG, используем MP3: {e}")
                with open(tmp_mp3_path, 'rb') as f:
                    audio_data = f.read()
                os.unlink(tmp_mp3_path)
            
            # Создаем BytesIO
            audio_buffer = BytesIO(audio_data)
            audio_buffer.seek(0)
            
            logger.info(f"Синтезирован голосовой ответ: {text[:50]}...")
            return audio_buffer
            
        except ImportError as e:
            logger.error(f"Не установлена зависимость: {e}. Установите: pip install gtts pydub")
            return None
        except Exception as e:
            logger.error(f"Ошибка синтеза речи: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_available(self) -> bool:
        """Проверить, доступны ли голосовые функции"""
        try:
            from gtts import gTTS
            # gTTS всегда доступен (онлайн)
            return True
        except ImportError:
            return False

