#include "pywrkgame/audio/AudioSystem.h"
#include <cmath>
#include <algorithm>
#include <fstream>
#include <cstring>

namespace pywrkgame {
namespace audio {

// Helper function to calculate distance
static float Distance(const Vec3& a, const Vec3& b) {
    float dx = a.x - b.x;
    float dy = a.y - b.y;
    float dz = a.z - b.z;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

// Helper function to calculate dot product
static float Dot(const Vec3& a, const Vec3& b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

AudioSystem::AudioSystem() 
    : initialized(false)
    , nextClipHandle(1)
    , nextSourceHandle(1)
    , nextMusicTrackHandle(1)
    , currentGameState(GameState::Menu)
    , currentMusicTrack(INVALID_MUSIC_TRACK)
    , currentMusicSource(INVALID_AUDIO_SOURCE)
{
}

AudioSystem::~AudioSystem() {
    if (initialized) {
        Shutdown();
    }
}

bool AudioSystem::Initialize(const AudioConfig& cfg) {
    if (initialized) {
        return false;
    }
    
    config = cfg;
    listener = AudioListenerData();
    initialized = true;
    return true;
}

void AudioSystem::Shutdown() {
    if (!initialized) return;
    
    // Stop adaptive music
    StopAdaptiveMusic();
    
    // Stop all sources
    for (auto& pair : audioSources) {
        if (pair.second->playing) {
            Stop(pair.first);
        }
    }
    
    // Clear all resources
    audioSources.clear();
    audioClips.clear();
    musicTracks.clear();
    
    initialized = false;
}

// Audio clip management
AudioClipHandle AudioSystem::LoadAudioClip(const std::string& filePath) {
    if (!initialized) return INVALID_AUDIO_CLIP;
    
    AudioFormat format = DetectAudioFormat(filePath);
    if (format == AudioFormat::Unknown) {
        return INVALID_AUDIO_CLIP;
    }
    
    auto clip = std::make_unique<AudioClip>();
    clip->filePath = filePath;
    clip->format = format;
    
    bool loaded = false;
    switch (format) {
        case AudioFormat::WAV:
            loaded = LoadWAV(filePath, *clip);
            break;
        case AudioFormat::MP3:
            loaded = LoadMP3(filePath, *clip);
            break;
        case AudioFormat::OGG:
            loaded = LoadOGG(filePath, *clip);
            break;
        case AudioFormat::FLAC:
            loaded = LoadFLAC(filePath, *clip);
            break;
        default:
            break;
    }
    
    if (!loaded) {
        return INVALID_AUDIO_CLIP;
    }
    
    AudioClipHandle handle = GenerateClipHandle();
    audioClips[handle] = std::move(clip);
    return handle;
}

void AudioSystem::UnloadAudioClip(AudioClipHandle handle) {
    if (!initialized) return;
    audioClips.erase(handle);
}

bool AudioSystem::IsClipValid(AudioClipHandle handle) const {
    return audioClips.find(handle) != audioClips.end();
}

AudioFormat AudioSystem::DetectAudioFormat(const std::string& filePath) const {
    size_t dotPos = filePath.find_last_of('.');
    if (dotPos == std::string::npos) {
        return AudioFormat::Unknown;
    }
    
    std::string ext = filePath.substr(dotPos + 1);
    std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
    
    if (ext == "wav") return AudioFormat::WAV;
    if (ext == "mp3") return AudioFormat::MP3;
    if (ext == "ogg") return AudioFormat::OGG;
    if (ext == "flac") return AudioFormat::FLAC;
    
    return AudioFormat::Unknown;
}

// Audio source management
AudioSourceHandle AudioSystem::CreateAudioSource(AudioClipHandle clipHandle) {
    if (!initialized || !IsClipValid(clipHandle)) {
        return INVALID_AUDIO_SOURCE;
    }
    
    auto source = std::make_unique<AudioSourceData>();
    source->clipHandle = clipHandle;
    
    AudioSourceHandle handle = GenerateSourceHandle();
    audioSources[handle] = std::move(source);
    return handle;
}

void AudioSystem::DestroyAudioSource(AudioSourceHandle handle) {
    if (!initialized) return;
    
    auto it = audioSources.find(handle);
    if (it != audioSources.end()) {
        if (it->second->playing) {
            Stop(handle);
        }
        audioSources.erase(it);
    }
}

bool AudioSystem::IsSourceValid(AudioSourceHandle handle) const {
    return audioSources.find(handle) != audioSources.end();
}

// Playback control
void AudioSystem::Play(AudioSourceHandle source) {
    if (!initialized || !IsSourceValid(source)) return;
    
    auto& sourceData = audioSources[source];
    sourceData->playing = true;
    sourceData->paused = false;
}

void AudioSystem::Pause(AudioSourceHandle source) {
    if (!initialized || !IsSourceValid(source)) return;
    
    auto& sourceData = audioSources[source];
    if (sourceData->playing) {
        sourceData->paused = true;
    }
}

void AudioSystem::Stop(AudioSourceHandle source) {
    if (!initialized || !IsSourceValid(source)) return;
    
    auto& sourceData = audioSources[source];
    sourceData->playing = false;
    sourceData->paused = false;
    sourceData->currentTime = 0.0f;
}

bool AudioSystem::IsPlaying(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return false;
    return audioSources.at(source)->playing && !audioSources.at(source)->paused;
}

bool AudioSystem::IsPaused(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return false;
    return audioSources.at(source)->paused;
}

// 3D positional audio
void AudioSystem::SetSourcePosition(AudioSourceHandle source, const Vec3& position) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->position = position;
}

Vec3 AudioSystem::GetSourcePosition(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return Vec3();
    return audioSources.at(source)->position;
}

void AudioSystem::SetSourceVelocity(AudioSourceHandle source, const Vec3& velocity) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->velocity = velocity;
}

Vec3 AudioSystem::GetSourceVelocity(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return Vec3();
    return audioSources.at(source)->velocity;
}

// Audio source properties
void AudioSystem::SetSourceVolume(AudioSourceHandle source, float volume) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->volume = std::max(0.0f, std::min(1.0f, volume));
}

float AudioSystem::GetSourceVolume(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return 0.0f;
    return audioSources.at(source)->volume;
}

void AudioSystem::SetSourcePitch(AudioSourceHandle source, float pitch) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->pitch = std::max(0.1f, std::min(4.0f, pitch));
}

float AudioSystem::GetSourcePitch(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return 1.0f;
    return audioSources.at(source)->pitch;
}

void AudioSystem::SetSourceLooping(AudioSourceHandle source, bool looping) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->looping = looping;
}

bool AudioSystem::IsSourceLooping(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return false;
    return audioSources.at(source)->looping;
}

// Audio effects
void AudioSystem::SetSourceEffect(AudioSourceHandle source, AudioEffect effect) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->effect = effect;
}

AudioEffect AudioSystem::GetSourceEffect(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return AudioEffect::None;
    return audioSources.at(source)->effect;
}

// Effect parameters
void AudioSystem::SetReverbParams(AudioSourceHandle source, const ReverbParams& params) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->reverbParams = params;
}

ReverbParams AudioSystem::GetReverbParams(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return ReverbParams();
    return audioSources.at(source)->reverbParams;
}

void AudioSystem::SetEchoParams(AudioSourceHandle source, const EchoParams& params) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->echoParams = params;
}

EchoParams AudioSystem::GetEchoParams(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return EchoParams();
    return audioSources.at(source)->echoParams;
}

void AudioSystem::SetDistortionParams(AudioSourceHandle source, const DistortionParams& params) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->distortionParams = params;
}

DistortionParams AudioSystem::GetDistortionParams(AudioSourceHandle source) const {
    if (!IsSourceValid(source)) return DistortionParams();
    return audioSources.at(source)->distortionParams;
}

// Real-time parameter modulation
void AudioSystem::ModulateReverbRoomSize(AudioSourceHandle source, float roomSize) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->reverbParams.roomSize = std::max(0.0f, std::min(1.0f, roomSize));
}

void AudioSystem::ModulateEchoDelay(AudioSourceHandle source, float delayTime) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->echoParams.delayTime = std::max(0.0f, std::min(5.0f, delayTime));
}

void AudioSystem::ModulateDistortionDrive(AudioSourceHandle source, float drive) {
    if (!initialized || !IsSourceValid(source)) return;
    audioSources[source]->distortionParams.drive = std::max(0.0f, std::min(1.0f, drive));
}

// Listener management
void AudioSystem::SetListenerPosition(const Vec3& position) {
    if (!initialized) return;
    listener.position = position;
}

Vec3 AudioSystem::GetListenerPosition() const {
    return listener.position;
}

void AudioSystem::SetListenerOrientation(const Vec3& forward, const Vec3& up) {
    if (!initialized) return;
    listener.forward = forward;
    listener.up = up;
}

void AudioSystem::GetListenerOrientation(Vec3& forward, Vec3& up) const {
    forward = listener.forward;
    up = listener.up;
}

void AudioSystem::SetListenerVelocity(const Vec3& velocity) {
    if (!initialized) return;
    listener.velocity = velocity;
}

Vec3 AudioSystem::GetListenerVelocity() const {
    return listener.velocity;
}

// HRTF processing
void AudioSystem::EnableHRTF(bool enable) {
    if (!initialized) return;
    config.enableHRTF = enable;
}

bool AudioSystem::IsHRTFEnabled() const {
    return config.enableHRTF;
}

// Master controls
void AudioSystem::SetMasterVolume(float volume) {
    if (!initialized) return;
    config.masterVolume = std::max(0.0f, std::min(1.0f, volume));
}

float AudioSystem::GetMasterVolume() const {
    return config.masterVolume;
}

// Adaptive music system
MusicTrackHandle AudioSystem::CreateMusicTrack(const std::string& name, AudioClipHandle clipHandle, GameState state) {
    if (!initialized || !IsClipValid(clipHandle)) {
        return INVALID_MUSIC_TRACK;
    }
    
    auto track = std::make_unique<MusicTrack>();
    track->name = name;
    track->clipHandle = clipHandle;
    track->associatedState = state;
    track->baseVolume = 1.0f;
    track->looping = true;
    
    MusicTrackHandle handle = GenerateMusicTrackHandle();
    musicTracks[handle] = std::move(track);
    return handle;
}

void AudioSystem::DestroyMusicTrack(MusicTrackHandle handle) {
    if (!initialized) return;
    
    // Stop music if this track is currently playing
    if (currentMusicTrack == handle) {
        StopAdaptiveMusic();
    }
    
    musicTracks.erase(handle);
}

bool AudioSystem::IsMusicTrackValid(MusicTrackHandle handle) const {
    return musicTracks.find(handle) != musicTracks.end();
}

void AudioSystem::PlayAdaptiveMusic(MusicTrackHandle track, GameState currentState) {
    if (!initialized || !IsMusicTrackValid(track)) return;
    
    currentGameState = currentState;
    
    // If already playing this track, do nothing
    if (currentMusicTrack == track && IsSourceValid(currentMusicSource) && IsPlaying(currentMusicSource)) {
        return;
    }
    
    // Stop current music if playing
    if (IsSourceValid(currentMusicSource)) {
        Stop(currentMusicSource);
        DestroyAudioSource(currentMusicSource);
        currentMusicSource = INVALID_AUDIO_SOURCE;
    }
    
    // Create new music source
    const auto& musicTrack = musicTracks[track];
    currentMusicSource = CreateAudioSource(musicTrack->clipHandle);
    
    if (currentMusicSource != INVALID_AUDIO_SOURCE) {
        SetSourceVolume(currentMusicSource, musicTrack->baseVolume);
        SetSourceLooping(currentMusicSource, musicTrack->looping);
        Play(currentMusicSource);
        currentMusicTrack = track;
    }
}

void AudioSystem::StopAdaptiveMusic() {
    if (!initialized) return;
    
    if (IsSourceValid(currentMusicSource)) {
        Stop(currentMusicSource);
        DestroyAudioSource(currentMusicSource);
        currentMusicSource = INVALID_AUDIO_SOURCE;
    }
    
    currentMusicTrack = INVALID_MUSIC_TRACK;
    activeTransition.active = false;
}

void AudioSystem::CrossfadeMusic(MusicTrackHandle newTrack, float duration) {
    if (!initialized || !IsMusicTrackValid(newTrack)) return;
    
    // Setup transition
    activeTransition.fromTrack = currentMusicTrack;
    activeTransition.toTrack = newTrack;
    activeTransition.duration = std::max(0.1f, duration);
    activeTransition.currentTime = 0.0f;
    activeTransition.active = true;
    
    // Create source for new track
    const auto& musicTrack = musicTracks[newTrack];
    AudioSourceHandle newSource = CreateAudioSource(musicTrack->clipHandle);
    
    if (newSource != INVALID_AUDIO_SOURCE) {
        SetSourceVolume(newSource, 0.0f); // Start at zero volume
        SetSourceLooping(newSource, musicTrack->looping);
        Play(newSource);
        
        // Store old source for crossfade
        // In a real implementation, we'd track both sources during transition
        // For simplicity, we'll just update the current source
        if (IsSourceValid(currentMusicSource)) {
            // Old source will fade out during transition
        }
        
        currentMusicSource = newSource;
        currentMusicTrack = newTrack;
    }
}

void AudioSystem::SetCurrentGameState(GameState state) {
    if (!initialized) return;
    currentGameState = state;
    
    // Automatically switch music based on game state
    // Find a track associated with this state
    for (const auto& pair : musicTracks) {
        if (pair.second->associatedState == state) {
            // Crossfade to this track
            CrossfadeMusic(pair.first, 2.0f);
            break;
        }
    }
}

GameState AudioSystem::GetCurrentGameState() const {
    return currentGameState;
}

MusicTrackHandle AudioSystem::GetCurrentMusicTrack() const {
    return currentMusicTrack;
}

bool AudioSystem::IsMusicPlaying() const {
    return IsSourceValid(currentMusicSource) && IsPlaying(currentMusicSource);
}

bool AudioSystem::IsCrossfading() const {
    return activeTransition.active;
}

// Update
void AudioSystem::Update(float deltaTime) {
    if (!initialized) return;
    
    // Update adaptive music
    UpdateAdaptiveMusic(deltaTime);
    
    for (auto& pair : audioSources) {
        auto& source = pair.second;
        
        if (!source->playing || source->paused) {
            continue;
        }
        
        // Update playback time
        source->currentTime += deltaTime * source->pitch;
        
        // Get clip duration
        auto clipIt = audioClips.find(source->clipHandle);
        if (clipIt != audioClips.end()) {
            float duration = clipIt->second->duration;
            
            if (source->currentTime >= duration) {
                if (source->looping) {
                    source->currentTime = std::fmod(source->currentTime, duration);
                } else {
                    Stop(pair.first);
                    continue;
                }
            }
        }
        
        // Apply 3D audio processing
        if (config.enableHRTF) {
            ProcessHRTF(*source, listener);
        }
        
        // Apply Doppler effect
        ApplyDopplerEffect(*source, listener);
        
        // Apply audio effects
        ProcessAudioEffects(*source, deltaTime);
    }
}

// Private helper methods
AudioClipHandle AudioSystem::GenerateClipHandle() {
    return nextClipHandle++;
}

AudioSourceHandle AudioSystem::GenerateSourceHandle() {
    return nextSourceHandle++;
}

MusicTrackHandle AudioSystem::GenerateMusicTrackHandle() {
    return nextMusicTrackHandle++;
}

bool AudioSystem::LoadWAV(const std::string& filePath, AudioClip& clip) {
    std::ifstream file(filePath, std::ios::binary);
    if (!file.is_open()) {
        return false;
    }
    
    // Simple WAV header parsing (44 bytes)
    char header[44];
    file.read(header, 44);
    
    if (std::strncmp(header, "RIFF", 4) != 0 || std::strncmp(header + 8, "WAVE", 4) != 0) {
        return false;
    }
    
    // Extract format information
    clip.channels = *reinterpret_cast<uint16_t*>(header + 22);
    clip.sampleRate = *reinterpret_cast<uint32_t*>(header + 24);
    clip.bitsPerSample = *reinterpret_cast<uint16_t*>(header + 34);
    
    // Read audio data
    uint32_t dataSize = *reinterpret_cast<uint32_t*>(header + 40);
    clip.data.resize(dataSize);
    file.read(reinterpret_cast<char*>(clip.data.data()), dataSize);
    
    // Calculate duration
    uint32_t bytesPerSample = clip.bitsPerSample / 8;
    uint32_t totalSamples = dataSize / (bytesPerSample * clip.channels);
    clip.duration = static_cast<float>(totalSamples) / clip.sampleRate;
    
    return true;
}

bool AudioSystem::LoadMP3(const std::string& filePath, AudioClip& clip) {
    // Simplified MP3 loading - in real implementation would use a library like minimp3
    std::ifstream file(filePath, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        return false;
    }
    
    size_t fileSize = file.tellg();
    file.seekg(0);
    
    clip.data.resize(fileSize);
    file.read(reinterpret_cast<char*>(clip.data.data()), fileSize);
    
    // Default values for MP3
    clip.sampleRate = 44100;
    clip.channels = 2;
    clip.bitsPerSample = 16;
    clip.duration = 1.0f; // Placeholder
    
    return true;
}

bool AudioSystem::LoadOGG(const std::string& filePath, AudioClip& clip) {
    // Simplified OGG loading - in real implementation would use a library like stb_vorbis
    std::ifstream file(filePath, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        return false;
    }
    
    size_t fileSize = file.tellg();
    file.seekg(0);
    
    clip.data.resize(fileSize);
    file.read(reinterpret_cast<char*>(clip.data.data()), fileSize);
    
    // Default values for OGG
    clip.sampleRate = 44100;
    clip.channels = 2;
    clip.bitsPerSample = 16;
    clip.duration = 1.0f; // Placeholder
    
    return true;
}

bool AudioSystem::LoadFLAC(const std::string& filePath, AudioClip& clip) {
    // Simplified FLAC loading - in real implementation would use libFLAC
    std::ifstream file(filePath, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        return false;
    }
    
    size_t fileSize = file.tellg();
    file.seekg(0);
    
    clip.data.resize(fileSize);
    file.read(reinterpret_cast<char*>(clip.data.data()), fileSize);
    
    // Default values for FLAC
    clip.sampleRate = 44100;
    clip.channels = 2;
    clip.bitsPerSample = 16;
    clip.duration = 1.0f; // Placeholder
    
    return true;
}

void AudioSystem::ProcessHRTF(AudioSourceData& source, const AudioListenerData& listener) {
    // Calculate direction from listener to source
    Vec3 direction;
    direction.x = source.position.x - listener.position.x;
    direction.y = source.position.y - listener.position.y;
    direction.z = source.position.z - listener.position.z;
    
    float distance = Distance(source.position, listener.position);
    if (distance > 0.001f) {
        direction.x /= distance;
        direction.y /= distance;
        direction.z /= distance;
    }
    
    // Calculate azimuth angle (horizontal angle)
    float azimuth = std::atan2(direction.x, direction.z);
    
    // Calculate elevation angle (vertical angle)
    float elevation = std::asin(direction.y);
    
    // Apply distance attenuation
    float attenuation = CalculateAttenuation(source.position, listener.position);
    source.volume *= attenuation;
    
    // HRTF processing would apply frequency-dependent filters based on azimuth and elevation
    // This is a simplified version - real HRTF would use measured impulse responses
}

float AudioSystem::CalculateAttenuation(const Vec3& sourcePos, const Vec3& listenerPos) const {
    float distance = Distance(sourcePos, listenerPos);
    
    // Inverse square law with minimum distance
    const float minDistance = 1.0f;
    const float maxDistance = 100.0f;
    
    if (distance < minDistance) {
        return 1.0f;
    }
    
    if (distance > maxDistance) {
        return 0.0f;
    }
    
    // Inverse square law attenuation
    float attenuation = minDistance / distance;
    return attenuation * attenuation;
}

void AudioSystem::ApplyDopplerEffect(AudioSourceData& source, const AudioListenerData& listener) {
    // Calculate relative velocity
    Vec3 relativeVelocity;
    relativeVelocity.x = source.velocity.x - listener.velocity.x;
    relativeVelocity.y = source.velocity.y - listener.velocity.y;
    relativeVelocity.z = source.velocity.z - listener.velocity.z;
    
    // Calculate direction from listener to source
    Vec3 direction;
    direction.x = source.position.x - listener.position.x;
    direction.y = source.position.y - listener.position.y;
    direction.z = source.position.z - listener.position.z;
    
    float distance = Distance(source.position, listener.position);
    if (distance < 0.001f) {
        return;
    }
    
    direction.x /= distance;
    direction.y /= distance;
    direction.z /= distance;
    
    // Calculate radial velocity (velocity along the line connecting listener and source)
    float radialVelocity = Dot(relativeVelocity, direction);
    
    // Speed of sound (m/s)
    const float speedOfSound = 343.0f;
    
    // Doppler shift factor
    float dopplerFactor = (speedOfSound - radialVelocity) / speedOfSound;
    
    // Clamp to reasonable range
    dopplerFactor = std::max(0.5f, std::min(2.0f, dopplerFactor));
    
    // Apply to pitch
    source.pitch *= dopplerFactor;
}

// Audio effect processing
void AudioSystem::ProcessAudioEffects(AudioSourceData& source, float deltaTime) {
    switch (source.effect) {
        case AudioEffect::Reverb:
            ApplyReverb(source);
            break;
        case AudioEffect::Echo:
            ApplyEcho(source, deltaTime);
            break;
        case AudioEffect::Distortion:
            ApplyDistortion(source);
            break;
        case AudioEffect::None:
        default:
            break;
    }
}

void AudioSystem::ApplyReverb(AudioSourceData& source) {
    // Simplified reverb simulation
    // In a real implementation, this would use a convolution reverb or
    // a network of comb and allpass filters (Freeverb algorithm)
    
    const ReverbParams& params = source.reverbParams;
    
    // Simulate room size effect on volume
    // Larger rooms have more reflections and longer decay
    float roomEffect = 1.0f - (params.roomSize * 0.3f);
    
    // Apply damping (high frequency absorption)
    float dampingEffect = 1.0f - (params.damping * 0.2f);
    
    // Combine wet and dry signals
    // In real implementation, wet signal would be the reverberated audio
    float effectiveVolume = (params.dryLevel + params.wetLevel * roomEffect * dampingEffect);
    source.volume *= effectiveVolume;
    
    // Width affects stereo spread (not implemented in this simplified version)
}

void AudioSystem::ApplyEcho(AudioSourceData& source, float deltaTime) {
    // Simplified echo/delay effect
    // In a real implementation, this would use a circular buffer to store
    // delayed samples and mix them back with feedback
    
    const EchoParams& params = source.echoParams;
    
    // Calculate number of echoes based on feedback
    // Higher feedback = more repetitions
    int numEchoes = static_cast<int>(params.feedback * 5.0f) + 1;
    
    // Simulate echo effect on volume
    // Each echo is quieter than the previous one
    float echoVolume = params.wetLevel;
    for (int i = 0; i < numEchoes; ++i) {
        echoVolume *= params.feedback;
    }
    
    // Combine wet and dry signals
    float effectiveVolume = params.dryLevel + echoVolume;
    source.volume *= effectiveVolume;
    
    // In real implementation, we would also modulate the delay time
    // based on deltaTime for dynamic echo effects
}

void AudioSystem::ApplyDistortion(AudioSourceData& source) {
    // Simplified distortion effect
    // In a real implementation, this would apply waveshaping/clipping
    // to the audio samples
    
    const DistortionParams& params = source.distortionParams;
    
    // Drive increases the gain before clipping
    // Higher drive = more distortion
    float driveGain = 1.0f + (params.drive * 3.0f);
    
    // Tone controls the frequency response
    // Lower tone = darker sound (more high frequency rolloff)
    float toneEffect = 0.7f + (params.tone * 0.3f);
    
    // Simulate distortion effect
    // In real implementation, this would clip/saturate the waveform
    float distortedVolume = std::min(1.0f, source.volume * driveGain) * toneEffect;
    
    // Combine wet and dry signals
    source.volume = params.dryLevel * source.volume + params.wetLevel * distortedVolume;
}

// Adaptive music processing
void AudioSystem::UpdateAdaptiveMusic(float deltaTime) {
    if (!initialized) return;
    
    // Process music transition if active
    if (activeTransition.active) {
        ProcessMusicTransition(deltaTime);
    }
}

void AudioSystem::ProcessMusicTransition(float deltaTime) {
    if (!activeTransition.active) return;
    
    activeTransition.currentTime += deltaTime;
    
    // Calculate crossfade progress (0.0 to 1.0)
    float progress = std::min(1.0f, activeTransition.currentTime / activeTransition.duration);
    
    // Apply crossfade volumes
    if (IsSourceValid(currentMusicSource)) {
        // New track fades in
        float newVolume = progress;
        
        if (IsMusicTrackValid(activeTransition.toTrack)) {
            const auto& track = musicTracks[activeTransition.toTrack];
            newVolume *= track->baseVolume;
        }
        
        SetSourceVolume(currentMusicSource, newVolume);
    }
    
    // Check if transition is complete
    if (progress >= 1.0f) {
        activeTransition.active = false;
        activeTransition.currentTime = 0.0f;
    }
}

} // namespace audio
} // namespace pywrkgame