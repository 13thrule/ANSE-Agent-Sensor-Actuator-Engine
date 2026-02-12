"""Data analysis tools that prove ANSE is using real captured data."""

import os
import json
import numpy as np
from typing import Dict, Any


async def analyze_frame(frame_id: str, frame_path: str) -> Dict[str, Any]:
    """
    Analyze a captured frame to prove we're using real data.
    Includes edge detection and color analysis.
    
    Args:
        frame_id: ID of the captured frame
        frame_path: Path to the JPEG file
        
    Returns:
        Analysis results with visual features
    """
    try:
        if not os.path.exists(frame_path):
            return {
                "status": "error",
                "message": f"Frame file not found: {frame_path}"
            }
        
        # Get file size (proves file exists and has content)
        file_size = os.path.getsize(frame_path)
        
        # Try advanced image analysis
        try:
            import cv2
            
            # Read image with OpenCV
            img = cv2.imread(frame_path)
            if img is None:
                return {
                    "status": "error",
                    "message": f"Could not read image: {frame_path}"
                }
            
            height, width = img.shape[:2]
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect edges using Canny
            edges = cv2.Canny(gray, 100, 200)
            edge_count = np.count_nonzero(edges)
            edge_percentage = (edge_count / (height * width)) * 100
            
            # Color analysis
            avg_color = cv2.mean(img)
            
            # Detect corners (Harris corner detection)
            corners = cv2.cornerHarris(gray, 2, 3, 0.04)
            corner_count = np.count_nonzero(corners > 0.01 * corners.max())
            
            # Histogram analysis
            hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])
            
            return {
                "status": "success",
                "frame_id": frame_id,
                "path": frame_path,
                "file_size_bytes": file_size,
                "resolution": f"{width}x{height}",
                "pixels": width * height,
                "edge_detection": {
                    "edges_found": int(edge_count),
                    "edge_density_percent": round(edge_percentage, 2)
                },
                "corner_detection": {
                    "corners_found": int(corner_count),
                    "corner_density": round(corner_count / (height * width) * 100, 4)
                },
                "color_analysis": {
                    "avg_blue": round(avg_color[0], 1),
                    "avg_green": round(avg_color[1], 1),
                    "avg_red": round(avg_color[2], 1)
                },
                "message": f"✓ Frame analyzed: {width}x{height} | {edge_count} edges | {corner_count} corners | Avg color BGR({avg_color[0]:.0f},{avg_color[1]:.0f},{avg_color[2]:.0f})"
            }
            
        except ImportError:
            # Fallback to PIL if OpenCV not available
            from PIL import Image
            img = Image.open(frame_path)
            width, height = img.size
            
            # Basic statistics
            if img.mode in ('RGB', 'RGBA'):
                img_array = np.array(img)
                avg_color = img_array.mean(axis=(0, 1))
                
                return {
                    "status": "success",
                    "frame_id": frame_id,
                    "path": frame_path,
                    "file_size_bytes": file_size,
                    "resolution": f"{width}x{height}",
                    "pixels": width * height,
                    "color_analysis": {
                        "avg_r": round(avg_color[0], 1),
                        "avg_g": round(avg_color[1], 1),
                        "avg_b": round(avg_color[2], 1)
                    },
                    "message": f"✓ Frame analyzed: {width}x{height} | Avg RGB({avg_color[0]:.0f},{avg_color[1]:.0f},{avg_color[2]:.0f})"
                }
            else:
                return {
                    "status": "success",
                    "frame_id": frame_id,
                    "path": frame_path,
                    "file_size_bytes": file_size,
                    "resolution": f"{width}x{height}",
                    "message": f"✓ Frame verified: {width}x{height} image ({file_size} bytes)"
                }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to analyze frame: {str(e)}"
        }


async def analyze_audio(audio_id: str, audio_path: str) -> Dict[str, Any]:
    """
    Analyze recorded audio with frequency analysis.
    
    Args:
        audio_id: ID of the recorded audio
        audio_path: Path to the WAV file
        
    Returns:
        Analysis results with audio features
    """
    try:
        if not os.path.exists(audio_path):
            return {
                "status": "error",
                "message": f"Audio file not found: {audio_path}"
            }
        
        # Get file size
        file_size = os.path.getsize(audio_path)
        
        try:
            import soundfile as sf
            import scipy.fft as fft
            
            data, samplerate = sf.read(audio_path)
            
            # Handle stereo to mono conversion
            if data.ndim > 1:
                data = data.mean(axis=1)
            
            duration_sec = len(data) / samplerate
            channels = 1 if data.ndim == 1 else data.ndim
            
            # Frequency analysis using FFT
            fft_result = fft.fft(data)
            freq_magnitude = np.abs(fft_result)
            freqs = fft.fftfreq(len(data), 1/samplerate)
            
            # Get dominant frequencies
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = freq_magnitude[:len(freqs)//2]
            
            top_freq_idx = np.argsort(positive_magnitude)[-5:][::-1]
            top_freqs = [int(positive_freqs[i]) for i in top_freq_idx if i < len(positive_freqs)]
            
            # Audio statistics
            rms = np.sqrt(np.mean(data**2))
            peak = np.max(np.abs(data))
            
            return {
                "status": "success",
                "audio_id": audio_id,
                "path": audio_path,
                "file_size_bytes": file_size,
                "duration_seconds": round(duration_sec, 2),
                "sample_rate": samplerate,
                "channels": int(channels),
                "samples": len(data),
                "audio_statistics": {
                    "rms_energy": round(rms, 4),
                    "peak_amplitude": round(peak, 4),
                    "dynamic_range_db": round(20 * np.log10(peak / (rms + 1e-10)), 2)
                },
                "frequency_analysis": {
                    "dominant_frequencies_hz": top_freqs,
                    "frequency_range": f"0-{samplerate//2}Hz"
                },
                "message": f"✓ Audio analyzed: {duration_sec:.2f}s at {samplerate}Hz | RMS: {rms:.4f} | Peak: {peak:.4f} | Dominant freqs: {top_freqs}"
            }
            
        except ImportError:
            # Fallback using wave module
            import wave
            with wave.open(audio_path, 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                duration = n_frames / framerate
                
                # Read audio data
                audio_data = wav_file.readframes(n_frames)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Basic statistics
                rms = np.sqrt(np.mean(audio_array**2))
                peak = np.max(np.abs(audio_array))
                
                return {
                    "status": "success",
                    "audio_id": audio_id,
                    "path": audio_path,
                    "file_size_bytes": file_size,
                    "duration_seconds": round(duration, 2),
                    "sample_rate": framerate,
                    "channels": n_channels,
                    "samples": n_frames,
                    "audio_statistics": {
                        "rms_energy": round(rms / 32768, 4),
                        "peak_amplitude": round(peak / 32768, 4)
                    },
                    "message": f"✓ Audio analyzed: {duration:.2f}s at {framerate}Hz | RMS: {rms/32768:.4f} | Peak: {peak/32768:.4f}"
                }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to analyze audio: {str(e)}"
        }


async def compare_frames(frame1_path: str, frame2_path: str) -> Dict[str, Any]:
    """
    Compare two frames using structural similarity.
    
    Args:
        frame1_path: Path to first frame
        frame2_path: Path to second frame
        
    Returns:
        Comparison results
    """
    try:
        if not os.path.exists(frame1_path) or not os.path.exists(frame2_path):
            return {
                "status": "error",
                "message": "One or both frame files not found"
            }
        
        file_size1 = os.path.getsize(frame1_path)
        file_size2 = os.path.getsize(frame2_path)
        
        try:
            import cv2
            from skimage.metrics import structural_similarity as ssim
            
            img1 = cv2.imread(frame1_path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(frame2_path, cv2.IMREAD_GRAYSCALE)
            
            if img1 is None or img2 is None:
                return {
                    "status": "error",
                    "message": "Could not read one or both images"
                }
            
            # Resize img2 to match img1 if different sizes
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Calculate SSIM
            similarity = ssim(img1, img2)
            
            return {
                "status": "success",
                "frame1_size": file_size1,
                "frame2_size": file_size2,
                "structural_similarity": round(similarity, 4),
                "difference_percent": round((1 - similarity) * 100, 2),
                "message": f"✓ Frames compared: SSIM={similarity:.4f} ({(1-similarity)*100:.2f}% different)"
            }
        except ImportError:
            # Fallback: simple size comparison
            different = file_size1 != file_size2
            
            return {
                "status": "success",
                "frame1_size": file_size1,
                "frame2_size": file_size2,
                "different": different,
                "message": f"✓ Frames compared: {file_size1} vs {file_size2} bytes - {'Different' if different else 'Similar'}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to compare frames: {str(e)}"
        }

