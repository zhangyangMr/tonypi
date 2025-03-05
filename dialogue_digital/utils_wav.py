import logging

import pyaudio
from pydub import AudioSegment
import io
import wave


def play_mp3_from_binary(mp3_binary_data):
    """播放mp3二进制音频数据"""
    wav_binary = mp3_to_wav_binary(mp3_binary_data)
    play_wav_from_binary(wav_binary)


def play_wav_from_binary(binary_data):
    """使用io.BytesIO将二进制数据转换为类文件对象,并直接播放二进制音频文件"""
    with io.BytesIO(binary_data) as wav_file:
        with wave.open(wav_file, 'rb') as wf:
            p = pyaudio.PyAudio()

            # 打开音频流
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )

            # 读取数据并播放
            data = wf.readframes(1024)  # 每次读取1024帧
            while data:
                stream.write(bytes(data))  # 播放音频数据
                data = wf.readframes(1024)  # 继续读取下一批数据

            # 停止并关闭音频流
            stream.stop_stream()
            stream.close()

        # 关闭PyAudio
        p.terminate()


def mp3_to_wav_binary(mp3_binary_data):
    """
    将 MP3 格式的二进制音频数据转换为 WAV 格式的二进制音频数据。
    :param mp3_binary_data: MP3 格式的二进制数据
    :return: WAV 格式的二进制数据
    """
    # 使用 io.BytesIO 将二进制数据转换为类文件对象
    mp3_file = io.BytesIO(mp3_binary_data)

    # 从 MP3 数据加载音频
    audio = AudioSegment.from_file(mp3_file, format="mp3")

    # 创建一个内存中的 WAV 文件
    wav_file = io.BytesIO()

    # 导出为 WAV 格式
    audio.export(wav_file, format="wav")

    # 获取 WAV 格式的二进制数据
    wav_binary_data = wav_file.getvalue()

    return wav_binary_data


# 1. 将 MP3 二进制数据写入文件
def save_mp3_to_file(mp3_binary_data, output_file_path):
    """
    将 MP3 格式的二进制音频数据保存为文件。
    :param mp3_binary_data: MP3 格式的二进制数据
    :param output_file_path: 输出文件路径
    """
    with open(output_file_path, "wb") as file:
        file.write(mp3_binary_data)
    logging.info(f"MP3 文件已保存到：{output_file_path}")


# 2. 将 MP3 文件转换为 WAV 格式
def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    """
    将 MP3 文件转换为 WAV 格式。
    :param mp3_file_path: MP3 文件路径
    :param wav_file_path: 输出的 WAV 文件路径
    """
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio.export(wav_file_path, format="wav")
    logging.info(f"WAV 文件已保存到：{wav_file_path}")


# 3. 播放 WAV 文件
def play_wav_file(wav_file_path):
    """
    播放 WAV 文件。
    :param wav_file_path: WAV 文件路径
    """
    with wave.open(wav_file_path, "rb") as wav_file:
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wav_file.getsampwidth()),
                        channels=wav_file.getnchannels(),
                        rate=wav_file.getframerate(),
                        output=True)

        data = wav_file.readframes(1024)
        while data:
            stream.write(data)
            data = wav_file.readframes(1024)

        stream.stop_stream()
        stream.close()
        p.terminate()
    logging.info("播放完成")


def play_mp3_file(mp3_binary_data):
    save_mp3_to_file(mp3_binary_data, "sound.mp3")
    convert_mp3_to_wav("sound.mp3", "sound.wav")
    play_wav_file("sound.wav")

# # 示例：从某个来源获取 MP3 二进制数据
# mp3_binary_data = b"..."  # 替换为实际的 MP3 二进制数据
#
# # 1. 保存 MP3 文件
# mp3_file_path = "output.mp3"
# save_mp3_to_file(mp3_binary_data, mp3_file_path)
#
# # 2. 转换为 WAV 文件
# wav_file_path = "output.wav"
# convert_mp3_to_wav(mp3_file_path, wav_file_path)
#
# # 3. 播放 WAV 文件
# play_wav_file(wav_file_path)
