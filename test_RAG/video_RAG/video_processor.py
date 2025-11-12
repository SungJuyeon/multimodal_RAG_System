"""영상 전처리: 프레임 추출, 오디오 추출, STT"""

import cv2
import os
import subprocess
from typing import List, Dict
import base64
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class VideoProcessor:
    def __init__(self, output_dir="./video_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def extract_audio(self, video_path: str) -> str:
        """FFmpeg로 오디오 추출"""
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(self.output_dir, f"{video_name}_audio.wav")
        
        # FFmpeg 명령어
        command = [
            'ffmpeg', '-i', video_path,
            '-vn',  # 비디오 스트림 제거
            '-acodec', 'pcm_s16le',  # 오디오 코덱
            '-ar', '16000',  # 샘플레이트
            '-ac', '1',  # 모노
            '-y',  # 덮어쓰기
            audio_path
        ]
        
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✓ 오디오 추출 완료: {audio_path}")
        return audio_path
    
    def extract_frames(self, video_path: str, fps: int = 1) -> List[Dict]:
        """OpenCV로 프레임 추출 (fps: 초당 추출할 프레임 수)"""
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(video_fps / fps)
        
        frames = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                timestamp = frame_count / video_fps
                frames.append({
                    'timestamp': timestamp,
                    'frame': frame,
                    'frame_number': frame_count
                })
            
            frame_count += 1
        
        cap.release()
        print(f"✓ 프레임 추출 완료: {len(frames)}개 프레임 (1fps)")
        return frames
    
    def detect_scene_changes(self, frames: List[Dict], threshold: float = 30.0) -> List[Dict]:
        """장면 전환 감지로 핵심 프레임 선택"""
        if not frames:
            return []
        
        key_frames = [frames[0]]  # 첫 프레임은 무조건 포함
        
        for i in range(1, len(frames)):
            prev_frame = frames[i-1]['frame']
            curr_frame = frames[i]['frame']
            
            # 프레임 간 차이 계산
            diff = cv2.absdiff(prev_frame, curr_frame)
            diff_score = diff.mean()
            
            if diff_score > threshold:  # 장면 전환 감지
                key_frames.append(frames[i])
        
        print(f"✓ 핵심 프레임 선택 완료: {len(key_frames)}개 (장면 전환 기준)")
        return key_frames
    
    def transcribe_audio(self, audio_path: str) -> List[Dict]:
        """Whisper API로 음성을 텍스트로 변환 (타임스탬프 포함)"""
        print("⏳ 음성 변환 중... (시간이 걸릴 수 있습니다)")
        
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        segments = []
        for segment in transcript.segments:
            segments.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text
            })
        
        print(f"✓ 음성 변환 완료: {len(segments)}개 세그먼트")
        return segments
    
    def process_video(self, video_path: str) -> tuple:
        """영상 전체 처리 파이프라인"""
        # 파일 존재 확인 추가
        if not os.path.exists(video_path):
            # 절대 경로로 변환 시도
            abs_path = os.path.abspath(video_path)
            print(f"❌ 영상 파일을 찾을 수 없습니다: {video_path}")
            print(f"절대 경로: {abs_path}")
            print(f"현재 디렉토리: {os.getcwd()}")
            raise FileNotFoundError(f"영상 파일이 존재하지 않습니다: {video_path}")
        
        print(f"\n{'='*60}")
        print(f"영상 처리 시작: {video_path}")
        print(f"{'='*60}\n")
        
        # 1. 오디오 추출
        audio_path = self.extract_audio(video_path)
        
        # 2. 프레임 추출
        all_frames = self.extract_frames(video_path, fps=1)
        
        # 3. 핵심 프레임 선택
        key_frames = self.detect_scene_changes(all_frames, threshold=25.0)
        
        # 4. 음성 → 텍스트
        text_segments = self.transcribe_audio(audio_path)
        
        print(f"\n{'='*60}")
        print("영상 처리 완료!")
        print(f"{'='*60}\n")
        
        return key_frames, text_segments