import librosa
import numpy as np
import sys
import os
import glob

def detect_key(audio_file_path, method='chroma_cqt', segment_analysis=True):
    # Load audio with higher precision
    try:
        y, sr = librosa.load(audio_file_path, sr=44100, mono=True, duration=60)
    except Exception as e:
        print(f"Error loading file {audio_file_path}: {str(e)}")
        return "Error"
    
    # Advanced tuning estimation
    try:
        tuning_offset = librosa.estimate_tuning(y=y, sr=sr, bins_per_octave=36)
        print(f"Detected tuning offset: {tuning_offset:.2f} semitones")
    except:
        tuning_offset = 0.0
    
    # Enhanced harmonic-percussive separation with focus on harmonics
    try:
        y_harmonic = librosa.effects.harmonic(y, margin=12)
    except:
        y_harmonic = y
    
    # Improved chroma extraction with tuning correction
    try:
        if method == 'chroma_cens':
            chromagram = librosa.feature.chroma_cens(y=y_harmonic, sr=sr, tuning=tuning_offset, n_chroma=12)
        else:
            chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr, tuning=tuning_offset, bins_per_octave=36)
    except:
        # Fallback to STFT if CQT fails
        chromagram = librosa.feature.chroma_stft(y=y_harmonic, sr=sr, tuning=tuning_offset)
    
    # Custom key profiles with enhanced minor key characteristics
    major_profile = np.array([7.0, 1.5, 4.0, 1.8, 5.0, 4.5, 1.8, 6.0, 2.0, 4.0, 1.5, 3.5])
    minor_profile = np.array([7.5, 3.0, 4.5, 7.0, 2.5, 4.5, 2.5, 6.0, 5.0, 2.5, 4.0, 4.0])
    
    try:
        # Normalize with robust scaling
        major_profile = (major_profile - np.median(major_profile)) / np.std(major_profile)
        minor_profile = (minor_profile - np.median(minor_profile)) / np.std(minor_profile)
    except:
        pass
    
    # Dynamic segment analysis with minor key focus
    try:
        if segment_analysis and chromagram.shape[1] > 10:
            n_segments = max(8, min(24, chromagram.shape[1] // 100))  # Adaptive segment count
            segment_keys = []
            
            # Compute RMS for weighting
            rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=512)[0]
            # Ensure rms has at least n_segments elements
            if len(rms) < n_segments:
                rms = np.pad(rms, (0, n_segments - len(rms)), mode='constant')
            
            # Compute harmonic content for weighting
            harmonic_content = librosa.effects.harmonic(y, margin=8)
            harmonic_rms = librosa.feature.rms(y=harmonic_content)[0]
            if len(harmonic_rms) < n_segments:
                harmonic_rms = np.pad(harmonic_rms, (0, n_segments - len(harmonic_rms)), mode='constant')
            
            for i in range(n_segments):
                start = i * chromagram.shape[1] // n_segments
                end = (i + 1) * chromagram.shape[1] // n_segments
                segment_chroma = np.mean(chromagram[:, start:end], axis=1)
                
                # Use median-based normalization for better outlier resistance
                chroma_median = np.median(segment_chroma)
                chroma_std = np.std(segment_chroma)
                if chroma_std > 1e-5:
                    segment_chroma = (segment_chroma - chroma_median) / chroma_std
                else:
                    segment_chroma = np.zeros_like(segment_chroma)
                
                key_idx, mode = _match_key(segment_chroma, major_profile, minor_profile)
                segment_keys.append((key_idx, mode))
            
            # Dual weighting: energy + harmonic content
            segment_weights = []
            rms_segments = np.array_split(rms, n_segments)
            harmonic_segments = np.array_split(harmonic_rms, n_segments)
            
            for i in range(n_segments):
                energy_weight = np.mean(rms_segments[i])
                harmonic_weight = np.mean(harmonic_segments[i])
                # Prioritize segments with high harmonic content
                combined_weight = energy_weight * harmonic_weight
                segment_weights.append(combined_weight)
            
            weighted_keys = {}
            for idx, key in enumerate(segment_keys):
                weighted_keys[key] = weighted_keys.get(key, 0) + segment_weights[idx]
            
            best_key = max(weighted_keys, key=weighted_keys.get)
            key_idx, mode = best_key
        else:
            mean_chroma = np.mean(chromagram, axis=1)
            chroma_std = np.std(mean_chroma)
            if chroma_std > 1e-5:
                mean_chroma = (mean_chroma - np.median(mean_chroma)) / chroma_std
            else:
                mean_chroma = np.zeros_like(mean_chroma)
            key_idx, mode = _match_key(mean_chroma, major_profile, minor_profile)
    except Exception as e:
        print(f"Error during key detection: {str(e)}")
        # Fallback: use simple mean chroma
        mean_chroma = np.mean(chromagram, axis=1)
        key_idx, mode = _match_key(mean_chroma, major_profile, minor_profile)

    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return keys[key_idx] + (' major key' if mode == 'major' else ' minor key')

def _match_key(chroma_vector, major_profile, minor_profile):
    max_corr = -np.inf
    best_key = 0
    best_mode = ''
    minor_boost = 1.08  # Slight boost for minor keys to improve detection
    
    # Handle all-zero vectors
    if np.all(chroma_vector == 0):
        return 0, 'major'
    
    for shift in range(12):
        # Major mode
        shifted_major = np.roll(major_profile, shift)
        try:
            corr_major = np.corrcoef(chroma_vector, shifted_major)[0, 1]
        except:
            corr_major = 0
        
        # Minor mode with boost
        shifted_minor = np.roll(minor_profile, shift)
        try:
            corr_minor = np.corrcoef(chroma_vector, shifted_minor)[0, 1] * minor_boost
        except:
            corr_minor = 0
        
        # Apply enharmonic boost for problematic keys
        enharmonic_boost = 1.0
        if shift in [1, 6]:  # C#/Db and F#/Gb positions
            enharmonic_boost = 1.35
        
        corr_major *= enharmonic_boost
        corr_minor *= enharmonic_boost
        
        # Check for best match
        if corr_major > max_corr:
            max_corr = corr_major
            best_key = shift
            best_mode = 'major'
        
        if corr_minor > max_corr:
            max_corr = corr_minor
            best_key = shift
            best_mode = 'minor'
    
    return best_key, best_mode

def process_directory(directory_path):
    # Supported audio file extensions
    audio_extensions = ['*.mp3', '*.wav', '*.flac', '*.ogg', '*.m4a', '*.aac']
    
    # Find all audio files in directory
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(directory_path, ext)))
    
    print(f"Found {len(audio_files)} audio files in directory")
    
    # Process each file
    for audio_file in audio_files:
        try:
            print(f"\nProcessing: {os.path.basename(audio_file)}")
            key = detect_key(audio_file)
            
            # Create output filename
            base_name = os.path.splitext(os.path.basename(audio_file))[0]
            output_file = os.path.join(directory_path, f"{base_name}_key.txt")
            
            # Write result to file
            with open(output_file, 'w') as f:
                f.write(key)
            
            print(f"Detected Key: {key} -> Saved to {output_file}")
            
        except Exception as e:
            print(f"Error processing {audio_file}: {str(e)}")
            # Write error to file
            base_name = os.path.splitext(os.path.basename(audio_file))[0]
            output_file = os.path.join(directory_path, f"{base_name}_key.txt")
            with open(output_file, 'w') as f:
                f.write(f"Error: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        print("Usage: python deepseek3.py <directory>")
        sys.exit(1)
    
    # Check if path is directory or file
    if os.path.isdir(target_path):
        process_directory(target_path)
    elif os.path.isfile(target_path):
        # Process single file
        try:
            key = detect_key(target_path)
            print(f"Detected Key: {key}")
            
            # Create output filename
            directory = os.path.dirname(target_path)
            base_name = os.path.splitext(os.path.basename(target_path))[0]
            output_file = os.path.join(directory, f"{base_name}_key.txt")
            
            # Write result to file
            with open(output_file, 'w') as f:
                f.write(key)
            
            print(f"Result saved to {output_file}")
        except Exception as e:
            print(f"Error processing file: {str(e)}")
    else:
        print(f"Path not found: {target_path}")
        sys.exit(1)