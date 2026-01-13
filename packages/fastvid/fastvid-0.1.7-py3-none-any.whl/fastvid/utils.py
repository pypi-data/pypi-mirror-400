# 音频频道调整：将音频向前/向后平移若干秒
def shift_audio(input_path, output_path, shift_seconds):
    """
    input_path: 输入视频文件路径
    output_path: 输出视频文件路径
    shift_seconds: 音频平移秒数，正数为向后，负数为向前
    """
    try:
        # 提取音频，平移后再合成
        temp_audio = os.path.join(
            os.path.dirname(output_path), f"temp_audio_{get_timestamp()}.aac"
        )
        temp_video = os.path.join(
            os.path.dirname(output_path), f"temp_video_{get_timestamp()}.mp4"
        )
        # 1. 提取音频
        cmd_extract = ["ffmpeg", "-i", input_path, "-vn", "-acodec", "copy", temp_audio]
        subprocess.run(cmd_extract, check=True)
        # 2. 平移音频
        if shift_seconds >= 0:
            # 向后平移，前面补静音
            cmd_shift = [
                "ffmpeg",
                "-i",
                temp_audio,
                "-af",
                f"adelay={int(shift_seconds * 1000)}|{int(shift_seconds * 1000)}",
                temp_audio + "_shift.aac",
            ]
        else:
            # 向前平移，裁剪前面
            cmd_shift = [
                "ffmpeg",
                "-ss",
                str(-shift_seconds),
                "-i",
                temp_audio,
                "-acodec",
                "copy",
                temp_audio + "_shift.aac",
            ]
        subprocess.run(cmd_shift, check=True)
        # 3. 提取无音频视频
        cmd_video = ["ffmpeg", "-i", input_path, "-an", "-vcodec", "copy", temp_video]
        subprocess.run(cmd_video, check=True)
        # 4. 合成新视频
        cmd_merge = [
            "ffmpeg",
            "-i",
            temp_video,
            "-i",
            temp_audio + "_shift.aac",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            output_path,
        ]
        subprocess.run(cmd_merge, check=True)
        print(
            f"{Colors.GREEN}音频平移完成！输出文件已保存到 {output_path}{Colors.RESET}"
        )
        os.remove(temp_audio)
        os.remove(temp_audio + "_shift.aac")
        os.remove(temp_video)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}音频平移失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
from datetime import datetime


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"


def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_media_duration(input_path):
    """获取媒体总时长（秒）。"""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_path,
        ]
        res = subprocess.run(cmd, check=True, capture_output=True)
        txt = res.stdout.decode().strip()
        if txt and txt.lower() != "nan":
            return float(txt)
    except Exception:
        return None


def has_video_stream(input_path):
    """检测输入是否包含至少一个视频流。"""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            input_path,
        ]
        res = subprocess.run(cmd, check=True, capture_output=True)
        out = res.stdout.decode().strip()
        return bool(out)
    except Exception:
        return False


# 视频加速转换
def accelerate_video(input_path, output_path, speed_factor):
    try:
        command = [
            "ffmpeg",
            "-i",
            input_path,
            "-vf",
            f"setpts=PTS/{speed_factor}",
            "-af",
            (
                f"atempo={speed_factor}"
                if speed_factor <= 2.0
                else "atempo=2.0,atempo={}".format(speed_factor / 2.0)
            ),
            "-strict",
            "-2",
            output_path,
        ]
        subprocess.run(command, check=True)
        print(
            f"{Colors.GREEN}加速转换完成！输出文件已保存到 {output_path}{Colors.RESET}"
        )
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}加速转换失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


# 视频转换为 GIF 动图（提高分辨率）
def convert_to_gif(input_path, output_path, fps=10, scale=1080):
    try:
        command = [
            "ffmpeg",
            "-i",
            input_path,
            "-vf",
            f"fps={fps},scale={scale}:-1:flags=lanczos",  # 使用 lanczos 缩放算法提高质量
            "-c:v",
            "gif",
            output_path,
        ]
        subprocess.run(command, check=True)
        print(
            f"{Colors.GREEN}GIF 转换完成！输出文件已保存到 {output_path}{Colors.RESET}"
        )
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}GIF 转换失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


# 视频压缩
def compress_video(input_path, output_path, crf=28):
    try:
        command = [
            "ffmpeg",
            "-i",
            input_path,
            "-vcodec",
            "libx264",
            "-crf",
            str(crf),
            output_path,
        ]
        subprocess.run(command, check=True)
        print(
            f"{Colors.GREEN}视频压缩完成！输出文件已保存到 {output_path}{Colors.RESET}"
        )
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}视频压缩失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


def resize_video(
    input_path,
    output_path,
    width,
    height,
    keep_aspect=True,
    fill_color="black",
):
    """调整视频尺寸，可选择保持纵横比（加黑边）或强制拉伸。"""
    try:
        if keep_aspect:
            filter_chain = (
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,"  # 等比缩放至目标框内
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:{fill_color}"  # 居中填充
            )
        else:
            filter_chain = f"scale={width}:{height}"  # 直接拉伸到目标尺寸

        command = [
            "ffmpeg",
            "-i",
            input_path,
            "-vf",
            filter_chain,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "copy",
            output_path,
        ]
        subprocess.run(command, check=True)
        mode = "保持纵横比" if keep_aspect else "拉伸填充"
        print(
            f"{Colors.GREEN}尺寸调整完成（{mode}）！输出文件已保存到 {output_path}{Colors.RESET}"
        )
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}尺寸调整失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


def crop_video(input_path, output_path, start_time, end_time):
    """
    裁剪视频，保留从 start_time 到 end_time 的部分
    :param input_path: 输入视频文件路径
    :param output_path: 输出视频文件路径
    :param start_time: 开始时间（秒）
    :param end_time: 结束时间（秒）
    """
    try:
        duration = end_time - start_time  # 计算裁剪的时长
        command = [
            "ffmpeg",
            "-i",
            input_path,
            "-ss",
            str(start_time),  # 开始时间
            "-t",
            str(duration),  # 裁剪时长
            "-c",
            "copy",  # 直接复制流，不重新编码
            output_path,
        ]
        subprocess.run(command, check=True)
        print(
            f"{Colors.GREEN}视频裁剪完成！输出文件已保存到 {output_path}{Colors.RESET}"
        )
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}视频裁剪失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


# 批量裁剪：支持对单个视频裁剪出多个片段，支持批量输入
def batch_crop_videos(input_paths, segments, output_dir):
    """
    input_paths: list of video file paths
    segments: list of (start, end) tuples，单位秒
    output_dir: 输出目录
    """
    results = []
    for input_path in input_paths:
        base = os.path.splitext(os.path.basename(input_path))[0]
        for idx, (start, end) in enumerate(segments):
            output_path = os.path.join(
                output_dir,
                f"{base}_part{idx + 1}_start{start}_end{end}_{get_timestamp()}.mp4",
            )
            crop_video(input_path, output_path, start, end)
            results.append(output_path)
    return results


# 视频合并：将多个视频片段合并为一个视频
def merge_videos(input_paths, output_path):
    """
    input_paths: list of video file paths
    output_path: 合并后输出文件路径
    """
    try:
        # 生成临时文件列表
        list_file = os.path.join(
            os.path.dirname(output_path), f"merge_list_{get_timestamp()}.txt"
        )
        with open(list_file, "w") as f:
            for path in input_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")
        command = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file,
            "-c",
            "copy",
            output_path,
        ]
        subprocess.run(command, check=True)
        print(
            f"{Colors.GREEN}视频合并完成！输出文件已保存到 {output_path}{Colors.RESET}"
        )
        os.remove(list_file)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}视频合并失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


# 多路视频栅格排布合并（xstack）
def stack_grid_videos(
    input_paths,
    output_path,
    rows,
    cols,
    tile_width,
    tile_height,
    audio_index=None,
    fill_color="black",
):
    """
    使用 ffmpeg xstack 将多路视频按网格排布合并为一个视频。

    input_paths: list[str] 输入视频文件路径列表，数量需等于 rows*cols
    output_path: 输出文件路径（例如 .mp4）
    rows, cols: 网格行、列数（例如 3,3 表示九宫格）
    tile_width, tile_height: 每个格子的目标分辨率（会按比例缩放并居中填充）
    audio_index: 选取作为输出音频的输入索引（None 为不保留音频）
    fill_color: 填充颜色（当缩放后留边时使用，例如 "black"）
    """
    try:
        total = rows * cols
        if len(input_paths) != total:
            raise ValueError(
                f"输入数量({len(input_paths)})与网格大小({rows}x{cols}={total})不匹配"
            )

        # 构建输入参数
        cmd = ["ffmpeg"]
        for p in input_paths:
            cmd.extend(["-i", p])

        # 计算各输入时长，确定最长，并为较短输入在尾部用黑帧补齐（tpad add）
        durations = []
        for p in input_paths:
            d = get_media_duration(p)
            durations.append(d if d is not None else 0.0)
        max_d = max(durations) if durations else 0.0

        # 为每路视频统一缩放到 tile，并居中填充到同尺寸；较短者追加 tpad 黑帧到最长
        scale_pad_parts = []
        for i in range(total):
            src_path = input_paths[i]
            delta = max(0.0, max_d - durations[i])
            if has_video_stream(src_path):
                # 使用源视频，缩放+居中填充；若较短则 tpad 补齐黑帧
                tpad = (
                    f",tpad=stop_mode=add:stop_duration={delta:.3f}"
                    if delta > 0.0
                    else ""
                )
                part = (
                    f"[{i}:v]scale={tile_width}:{tile_height}:force_original_aspect_ratio=decrease"
                    f",pad={tile_width}:{tile_height}:(ow-iw)/2:(oh-ih)/2:{fill_color}{tpad}[v{i}]"
                )
            else:
                # 无视频流：直接生成指定时长的纯色帧
                part = f"color=c={fill_color}:size={tile_width}x{tile_height}:rate=25:d={max_d:.3f}[v{i}]"
            scale_pad_parts.append(part)

        # 计算每个格子的左上角坐标并构建 layout
        layout_entries = []
        for i in range(total):
            r = i // cols
            c = i % cols
            x = c * tile_width
            y = r * tile_height
            layout_entries.append(f"{x}_{y}")

        # 将所有 [vN] 喂给 xstack
        v_labels = "".join([f"[v{i}]" for i in range(total)])
        layout_str = "|".join(layout_entries)
        # 仅使用 xstack 的基础选项，时长一致性由 tpad 保证
        xstack_part = f"{v_labels}xstack=inputs={total}:layout={layout_str}[v]"

        filter_complex = ";".join(scale_pad_parts + [xstack_part])

        cmd.extend(["-filter_complex", filter_complex])
        # 映射视频输出
        cmd.extend(["-map", "[v]"])

        # 可选映射音频（取某一路的音频）
        if audio_index is not None:
            cmd.extend(["-map", f"{audio_index}:a?"])
            cmd.extend(["-c:a", "aac"])  # 统一音频编码

        # 视频编码参数（可根据需要调整）
        cmd.extend(
            ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", output_path]
        )

        subprocess.run(cmd, check=True)
        print(
            f"{Colors.GREEN}栅格合并完成！输出文件已保存到 {output_path}{Colors.RESET}"
        )
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}栅格合并失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


# 多行可变列栅格排布（如上3、下2）
def stack_grid_videos_rows(
    input_paths,
    output_path,
    row_counts,
    tile_width,
    tile_height,
    audio_index=None,
    stretch_fill=False,
    fill_color="black",
):
    """按行布局合并多路视频，可选强制拉伸填满整行。"""

    try:
        total = sum(row_counts)
        if len(input_paths) != total:
            raise ValueError(f"输入数量({len(input_paths)})与行布局总数({total})不匹配")

        if not row_counts:
            raise ValueError("行计数列表不能为空")

        max_cols = max(row_counts)
        if max_cols <= 0:
            raise ValueError("行计数必须为正整数")

        # 构建输入参数
        cmd = ["ffmpeg"]
        for p in input_paths:
            cmd.extend(["-i", p])

        # 时长分析
        durations = []
        for p in input_paths:
            d = get_media_duration(p)
            durations.append(d if d is not None else 0.0)
        max_d = max(durations) if durations else 0.0

        # 预计算每个视频的目标尺寸与布局
        target_sizes = []
        layout_entries = []
        total_row_width = max_cols * tile_width
        for r, cols in enumerate(row_counts):
            if cols <= 0:
                raise ValueError("行计数必须为正整数")

            if stretch_fill:
                base_width = total_row_width // cols
                remainder = total_row_width - base_width * cols
                x = 0
                for c in range(cols):
                    width = base_width + (1 if c < remainder else 0)
                    target_sizes.append((width, tile_height))
                    layout_entries.append(f"{x}_{r * tile_height}")
                    x += width
            else:
                left_offset = ((max_cols - cols) * tile_width) // 2
                for c in range(cols):
                    target_sizes.append((tile_width, tile_height))
                    x = left_offset + c * tile_width
                    layout_entries.append(f"{x}_{r * tile_height}")

        # 缩放与时间对齐；若无视频流则生成纯色帧
        scale_pad_parts = []
        for i, (target_w, target_h) in enumerate(target_sizes):
            src_path = input_paths[i]
            delta = max(0.0, max_d - durations[i])
            if has_video_stream(src_path):
                filters = []
                if stretch_fill:
                    filters.append(f"[{i}:v]scale={target_w}:{target_h}")
                else:
                    filters.append(
                        f"[{i}:v]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease"
                    )
                    filters.append(
                        f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:{fill_color}"
                    )
                if delta > 0.0:
                    filters.append(f"tpad=stop_mode=add:stop_duration={delta:.3f}")
                part = ",".join(filters) + f"[v{i}]"
            else:
                part = f"color=c={fill_color}:size={target_w}x{target_h}:rate=25:d={max_d:.3f}[v{i}]"
            scale_pad_parts.append(part)

        v_labels = "".join([f"[v{i}]" for i in range(total)])
        layout_str = "|".join(layout_entries)
        xstack_part = f"{v_labels}xstack=inputs={total}:layout={layout_str}[v]"

        filter_complex = ";".join(scale_pad_parts + [xstack_part])
        cmd.extend(["-filter_complex", filter_complex])
        cmd.extend(["-map", "[v]"])

        if audio_index is not None:
            cmd.extend(["-map", f"{audio_index}:a?"])
            cmd.extend(["-c:a", "aac"])

        cmd.extend(
            ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", output_path]
        )

        subprocess.run(cmd, check=True)
        print(
            f"{Colors.GREEN}可变行栅格合并完成！输出文件已保存到 {output_path}{Colors.RESET}"
        )
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}栅格合并失败：{e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}发生错误：{e}{Colors.RESET}")


# 获取文件夹中的视频文件
def get_video_files(folder_path):
    video_extensions = [".mp4", ".mkv", ".avi", ".mov"]
    video_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if os.path.splitext(file)[1].lower() in video_extensions:
                video_files.append(os.path.join(root, file))
    return video_files


# GUI 界面
class VideoToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频处理工具")
        # 调整默认尺寸：增加高度，收窄宽度，便于显示控件
        self.root.geometry("1150x1020")

        # 输入文件选择
        self.input_file_label = tk.Label(root, text="选择视频文件或文件夹：")
        self.input_file_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.input_file_entry = tk.Entry(root, width=50)
        self.input_file_entry.grid(row=0, column=1, padx=10, pady=10)

        self.input_file_button = tk.Button(
            root, text="浏览", width=10, command=self.select_input
        )
        self.input_file_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        # 输出路径选择（调整到第 2 行）
        self.output_folder_label = tk.Label(root, text="选择输出文件夹（可选）：")
        self.output_folder_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.output_folder_entry = tk.Entry(root, width=50)
        self.output_folder_entry.grid(row=1, column=1, padx=10, pady=10)

        self.output_folder_button = tk.Button(
            root, text="浏览", width=10, command=self.select_output_folder
        )
        self.output_folder_button.grid(row=1, column=2, padx=10, pady=10, sticky="w")

        # 加速转换（调整到第 3 行）
        self.speed_label = tk.Label(root, text="加速倍数：")
        self.speed_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.speed_entry = tk.Entry(root, width=10)
        self.speed_entry.insert(0, "4.0")  # 默认加速倍数
        self.speed_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.accelerate_button = tk.Button(
            root, text="加速转换", width=10, command=self.start_accelerate
        )
        self.accelerate_button.grid(row=2, column=2, padx=10, pady=10, sticky="w")

        # 转换为 GIF（调整到第 4 行）
        self.gif_label = tk.Label(root, text="GIF 分辨率（宽度）：")
        self.gif_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

        self.gif_entry = tk.Entry(root, width=10)
        self.gif_entry.insert(0, "1080")  # 默认分辨率宽度
        self.gif_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.gif_button = tk.Button(
            root, text="转换为 GIF", width=10, command=self.start_gif_conversion
        )
        self.gif_button.grid(row=3, column=2, padx=10, pady=10, sticky="w")

        # 视频压缩（调整到第 5 行）
        self.compress_label = tk.Label(
            root, text="压缩质量（CRF，0-51，越小质量越高）："
        )
        self.compress_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")

        self.compress_entry = tk.Entry(root, width=10)
        self.compress_entry.insert(0, "28")
        self.compress_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.compress_button = tk.Button(
            root, text="压缩视频", width=10, command=self.start_compression
        )
        self.compress_button.grid(row=4, column=2, padx=10, pady=10, sticky="w")

        # 裁剪视频（调整到第 6 行）
        self.crop_label = tk.Label(root, text="裁剪视频（开始时间 结束时间，秒）：")
        self.crop_label.grid(row=5, column=0, padx=10, pady=10, sticky="e")

        self.crop_start_entry = tk.Entry(root, width=10)
        self.crop_start_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        self.crop_end_entry = tk.Entry(root, width=10)
        self.crop_end_entry.grid(row=5, column=1, padx=(100, 10), pady=10, sticky="w")

        self.crop_button = tk.Button(
            root, text="裁剪视频", width=10, command=self.start_crop
        )
        self.crop_button.grid(row=5, column=2, padx=10, pady=10, sticky="w")

        # 批量裁剪（第7行）
        self.batch_crop_label = tk.Label(
            root, text="批量裁剪（开始1,结束1,开始2,结束2,...，秒）："
        )
        self.batch_crop_label.grid(row=6, column=0, padx=10, pady=10, sticky="e")
        self.batch_crop_entry = tk.Entry(root, width=40)
        self.batch_crop_entry.grid(row=6, column=1, padx=10, pady=10, sticky="w")
        self.batch_crop_button = tk.Button(
            root, text="批量裁剪", width=10, command=self.start_batch_crop
        )
        self.batch_crop_button.grid(row=6, column=2, padx=10, pady=10, sticky="w")

        # 视频合并（第8行）

        self.merge_label = tk.Label(root, text="合并视频文件夹：")
        self.merge_label.grid(row=7, column=0, padx=10, pady=10, sticky="e")
        self.merge_entry = tk.Entry(root, width=40)
        self.merge_entry.grid(row=7, column=1, padx=10, pady=10, sticky="w")
        self.merge_browse_button = tk.Button(
            root, text="浏览", width=10, command=self.select_merge_folder
        )
        self.merge_browse_button.grid(row=7, column=2, padx=10, pady=10, sticky="w")
        self.merge_out_label = tk.Label(root, text="合并输出文件名：")
        self.merge_out_label.grid(row=8, column=0, padx=10, pady=10, sticky="e")
        self.merge_out_entry = tk.Entry(root, width=40)
        self.merge_out_entry.grid(row=8, column=1, padx=10, pady=10, sticky="w")
        self.merge_button = tk.Button(
            root, text="合并视频", width=10, command=self.start_merge
        )
        self.merge_button.grid(row=8, column=2, padx=10, pady=10, sticky="w")

        # 音频平移（第9行）
        self.shift_audio_label = tk.Label(root, text="音频平移（秒，正为后，负为前）：")
        self.shift_audio_label.grid(row=9, column=0, padx=10, pady=10, sticky="e")
        self.shift_audio_entry = tk.Entry(root, width=10)
        self.shift_audio_entry.grid(row=9, column=1, padx=10, pady=10, sticky="w")
        self.shift_audio_button = tk.Button(
            root, text="音频平移", width=10, command=self.start_shift_audio
        )
        self.shift_audio_button.grid(row=9, column=2, padx=10, pady=10, sticky="w")

        # 栅格（xstack）合并（第10-15行）
        # 栅格合并区域已复用顶部输入选择，无需额外提示

        self.rows_count_label = tk.Label(root, text="行计数列表（如 1,3 2,2）：")
        self.rows_count_label.grid(row=11, column=0, padx=10, pady=10, sticky="e")
        self.rows_count_entry = tk.Entry(root, width=20)
        self.rows_count_entry.grid(row=11, column=1, padx=10, pady=10, sticky="w")

        self.tile_label = tk.Label(root, text="每格宽/高：")
        self.tile_label.grid(row=12, column=0, padx=10, pady=10, sticky="e")
        self.tile_w_entry = tk.Entry(root, width=10)
        self.tile_w_entry.insert(0, "640")
        self.tile_w_entry.grid(row=12, column=1, padx=10, pady=10, sticky="w")
        self.tile_h_entry = tk.Entry(root, width=10)
        self.tile_h_entry.insert(0, "480")
        self.tile_h_entry.grid(row=12, column=1, padx=(120, 10), pady=10, sticky="w")

        self.stack_stretch_var = tk.BooleanVar(value=False)
        self.stack_stretch_check = tk.Checkbutton(
            root,
            text="填满格子（强制拉伸）",
            variable=self.stack_stretch_var,
        )
        self.stack_stretch_check.grid(row=12, column=2, padx=10, pady=10, sticky="w")

        self.stack_audio_label = tk.Label(root, text="音轨索引（可选）：")
        self.stack_audio_label.grid(row=13, column=0, padx=10, pady=10, sticky="e")
        self.stack_audio_entry = tk.Entry(root, width=10)
        self.stack_audio_entry.grid(row=13, column=1, padx=10, pady=10, sticky="w")

        self.stack_button = tk.Button(
            root, text="执行栅格合并", width=14, command=self.start_stack_merge
        )
        self.stack_button.grid(row=15, column=2, padx=10, pady=10, sticky="w")

        # 尺寸调整（追加在底部）
        self.resize_label = tk.Label(root, text="尺寸调整（输出画布宽 高）：")
        self.resize_label.grid(row=16, column=0, padx=10, pady=10, sticky="e")
        self.resize_width_entry = tk.Entry(root, width=10)
        self.resize_width_entry.insert(0, "1920")
        self.resize_width_entry.grid(row=16, column=1, padx=10, pady=10, sticky="w")
        self.resize_height_entry = tk.Entry(root, width=10)
        self.resize_height_entry.insert(0, "1080")
        self.resize_height_entry.grid(
            row=16, column=1, padx=(120, 10), pady=10, sticky="w"
        )

        self.resize_keep_var = tk.BooleanVar(value=True)
        self.resize_keep_check = tk.Checkbutton(
            root,
            text="保持纵横比（加填充）",
            variable=self.resize_keep_var,
        )
        self.resize_keep_check.grid(row=17, column=1, padx=10, pady=5, sticky="w")

        self.resize_hint_label = tk.Label(
            root,
            text="保持纵横比：按原比例适配画布并补边",
            fg="#555555",
        )
        self.resize_hint_label.grid(row=18, column=1, padx=10, pady=(0, 5), sticky="w")

        self.resize_fill_label = tk.Label(root, text="填充颜色（fit 模式）：")
        self.resize_fill_label.grid(row=17, column=0, padx=10, pady=5, sticky="e")
        self.resize_fill_entry = tk.Entry(root, width=10)
        self.resize_fill_entry.insert(0, "black")
        self.resize_fill_entry.grid(
            row=17, column=1, padx=(150, 10), pady=5, sticky="w"
        )

        self.resize_button = tk.Button(
            root, text="调整尺寸", width=10, command=self.start_resize
        )
        self.resize_button.grid(row=19, column=2, padx=10, pady=10, sticky="w")

    def select_merge_folder(self):
        folder_path = filedialog.askdirectory(title="选择要合并的视频文件夹")
        if folder_path:
            self.merge_entry.delete(0, tk.END)
            self.merge_entry.insert(0, folder_path)
        # 仅更新合并文件夹选择，无需重复创建音频平移控件

    def start_batch_crop(self):
        inputs = self.resolve_input_targets()
        if inputs is None:
            return

        video_files = self.collect_video_files(inputs)
        if not video_files:
            messagebox.showerror("错误", "未找到可处理的视频文件！")
            return

        output_folder = self.get_output_folder()
        segs = (
            self.batch_crop_entry.get().replace("，", ",").replace("-", ",").split(",")
        )
        try:
            segs = [float(s.strip()) for s in segs if s.strip()]
            if len(segs) % 2 != 0:
                messagebox.showerror("错误", "批量裁剪参数必须成对出现！")
                return
            segments = [(segs[i], segs[i + 1]) for i in range(0, len(segs), 2)]
        except Exception:
            messagebox.showerror("错误", "批量裁剪参数格式错误！")
            return
        batch_crop_videos(video_files, segments, output_folder)

    def start_merge(self):
        folder = self.merge_entry.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("错误", "请先选择要合并的视频文件夹！")
            return
        video_files = get_video_files(folder)
        if not video_files:
            messagebox.showerror("错误", "该文件夹下未找到可合并的视频文件！")
            return
        out_file = self.merge_out_entry.get().strip()
        if not out_file:
            # 自动生成输出文件名
            base = os.path.basename(os.path.normpath(folder))
            out_file = os.path.join(folder, f"{base}_merged_{get_timestamp()}.mp4")
            self.merge_out_entry.insert(0, out_file)
        merge_videos(video_files, out_file)

    def start_shift_audio(self):
        inputs = self.resolve_input_targets()
        if inputs is None:
            return
        video_files = self.collect_video_files(inputs)
        if not video_files:
            messagebox.showerror("错误", "未找到可处理的视频文件！")
            return
        output_folder = self.get_output_folder()
        try:
            shift = float(self.shift_audio_entry.get())
        except Exception:
            messagebox.showerror("错误", "音频平移参数格式错误！")
            return
        for video_file in video_files:
            output_path = os.path.join(
                output_folder,
                f"{os.path.splitext(os.path.basename(video_file))[0]}_shift{shift}_{get_timestamp()}.mp4",
            )
            shift_audio(video_file, output_path, shift)

    def start_crop(self):
        inputs = self.resolve_input_targets()
        if inputs is None:
            return

        video_files = self.collect_video_files(inputs)
        if not video_files:
            messagebox.showerror("错误", "未找到可处理的视频文件！")
            return

        output_folder = self.get_output_folder()
        start_time = float(self.crop_start_entry.get())
        end_time = float(self.crop_end_entry.get())

        for video_file in video_files:
            output_path = os.path.join(
                output_folder,
                f"{os.path.splitext(os.path.basename(video_file))[0]}_start{start_time}_end{end_time}_{get_timestamp()}.mp4",
            )
            crop_video(video_file, output_path, start_time, end_time)

    def select_input(self):
        selected_files = filedialog.askopenfilenames(
            title="选择视频文件（可多选）",
            filetypes=[("视频文件", "*.mp4 *.mkv *.avi *.mov")],
        )
        paths = list(selected_files)
        if not paths:
            directory = filedialog.askdirectory(title="选择视频文件夹")
            if directory:
                paths = [directory]
        if not paths:
            return

        cleaned = [p.rstrip("*").strip() for p in paths if p]
        if not cleaned:
            return

        joined = ";".join(cleaned)
        self.input_file_entry.delete(0, tk.END)
        self.input_file_entry.insert(0, joined)

        first = cleaned[0]
        if os.path.isfile(first):
            default_output = os.path.dirname(first)
        elif os.path.isdir(first):
            default_output = first
        else:
            default_output = ""

        if default_output:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, default_output)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, folder_path)

    def get_output_folder(self):
        # 若未显式指定，默认使用首个输入路径所在目录
        output_folder = self.output_folder_entry.get().strip()
        if output_folder:
            return output_folder

        inputs = self.resolve_input_targets(show_error=False)
        if inputs:
            first = inputs[0]
            if os.path.isfile(first):
                return os.path.dirname(first) or os.getcwd()
            if os.path.isdir(first):
                return first
        return os.getcwd()

    def resolve_input_targets(self, show_error=True):
        raw = self.input_file_entry.get().strip()
        if not raw:
            if show_error:
                messagebox.showerror("错误", "请先选择视频文件或文件夹！")
            return None

        normalized = raw.replace("；", ";").replace("\n", ";")
        candidates = [p.strip() for p in normalized.split(";") if p.strip()]
        if not candidates:
            if show_error:
                messagebox.showerror("错误", "请输入有效的文件或文件夹路径！")
            return None

        for path in candidates:
            if not os.path.exists(path):
                if show_error:
                    messagebox.showerror("错误", f"路径不存在：{path}")
                return None
        return candidates

    def collect_video_files(self, inputs):
        video_files = []
        for path in inputs:
            if os.path.isdir(path):
                files = get_video_files(path)
                files.sort()
                video_files.extend(files)
            else:
                video_files.append(path)
        return video_files

    def start_accelerate(self):
        inputs = self.resolve_input_targets()
        if inputs is None:
            return

        video_files = self.collect_video_files(inputs)
        if not video_files:
            messagebox.showerror("错误", "未找到可处理的视频文件！")
            return

        output_folder = self.get_output_folder()
        speed_factor = float(self.speed_entry.get())

        for video_file in video_files:
            output_path = os.path.join(
                output_folder,
                f"{os.path.splitext(os.path.basename(video_file))[0]}_{get_timestamp()}_x{speed_factor}_accelerate.mp4",
            )
            accelerate_video(video_file, output_path, speed_factor)

    def start_gif_conversion(self):
        inputs = self.resolve_input_targets()
        if inputs is None:
            return

        video_files = self.collect_video_files(inputs)
        if not video_files:
            messagebox.showerror("错误", "未找到可处理的视频文件！")
            return

        output_folder = self.get_output_folder()
        scale = int(self.gif_entry.get())

        for video_file in video_files:
            output_path = os.path.join(
                output_folder,
                f"{os.path.splitext(os.path.basename(video_file))[0]}_{get_timestamp()}_{scale}_gif.gif",
            )
            convert_to_gif(video_file, output_path, scale=scale)

    def start_compression(self):
        inputs = self.resolve_input_targets()
        if inputs is None:
            return

        video_files = self.collect_video_files(inputs)
        if not video_files:
            messagebox.showerror("错误", "未找到可处理的视频文件！")
            return

        output_folder = self.get_output_folder()
        crf = int(self.compress_entry.get())

        for video_file in video_files:
            output_path = os.path.join(
                output_folder,
                f"{os.path.splitext(os.path.basename(video_file))[0]}_{get_timestamp()}_crf{crf}_compress.mp4",
            )
            compress_video(video_file, output_path, crf)

    def start_stack_merge(self):
        inputs = self.resolve_input_targets()
        if inputs is None:
            return

        input_paths = self.collect_video_files(inputs)
        if not input_paths:
            messagebox.showerror("错误", "未找到可用于栅格合并的视频文件！")
            return
        # 优先使用可变行布局（rows counts）
        rows_counts_text = self.rows_count_entry.get().strip()
        try:
            tile_w = int(self.tile_w_entry.get())
            tile_h = int(self.tile_h_entry.get())
        except Exception:
            messagebox.showerror("错误", "每格尺寸必须为整数！")
            return

        audio_index = None
        ai = self.stack_audio_entry.get().strip()
        if ai:
            try:
                audio_index = int(ai)
            except Exception:
                messagebox.showerror("错误", "音轨索引必须为整数！")
                return

        stretch_fill = self.stack_stretch_var.get()

        if not rows_counts_text:
            messagebox.showerror(
                "错误",
                "请填写行计数列表，例如 1,3 2,2 或 (1,3) (2,2)。",
            )
            return

        # 解析 (row,count) 列表（支持括号与逗号分隔）
        tokens = rows_counts_text.strip().split()
        pairs = []
        try:
            for tok in tokens:
                s = tok.strip().strip("()[]")
                a, b = s.split(",")
                row_idx = int(a)
                cnt = int(b)
                pairs.append((row_idx, cnt))
        except Exception:
            messagebox.showerror(
                "错误", "行计数列表格式错误（示例：1,3 2,2 或 (1,3) (2,2)）！"
            )
            return
        pairs.sort(key=lambda x: x[0])
        row_counts = [cnt for _, cnt in pairs]
        if sum(row_counts) != len(input_paths):
            messagebox.showerror(
                "错误",
                f"所选视频数量({len(input_paths)})与行布局总数({sum(row_counts)})不匹配！",
            )
            return
        output_folder = self.get_output_folder()
        layout_tag = "_".join(map(str, row_counts))
        out_path = os.path.join(
            output_folder,
            f"stack_rows_{layout_tag}_{get_timestamp()}.mp4",
        )
        stack_grid_videos_rows(
            input_paths,
            out_path,
            row_counts,
            tile_w,
            tile_h,
            audio_index=audio_index,
            stretch_fill=stretch_fill,
        )

    def start_resize(self):
        inputs = self.resolve_input_targets()
        if inputs is None:
            return

        video_files = self.collect_video_files(inputs)
        if not video_files:
            messagebox.showerror("错误", "未找到可处理的视频文件！")
            return

        try:
            width = int(self.resize_width_entry.get())
            height = int(self.resize_height_entry.get())
            if width <= 0 or height <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("错误", "目标宽高必须为正整数！")
            return

        keep_aspect = self.resize_keep_var.get()
        fill_color = self.resize_fill_entry.get().strip() or "black"
        output_folder = self.get_output_folder()
        mode = "fit" if keep_aspect else "stretch"

        for path in video_files:
            base = os.path.splitext(os.path.basename(path))[0]
            output_path = os.path.join(
                output_folder,
                f"{base}_{width}x{height}_{mode}_{get_timestamp()}.mp4",
            )
            resize_video(
                path,
                output_path,
                width,
                height,
                keep_aspect=keep_aspect,
                fill_color=fill_color,
            )
