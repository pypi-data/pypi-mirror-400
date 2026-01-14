#pragma once

#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <cstdint>

namespace pywrkgame {
namespace audio {

// Forward declarations
struct AudioClip;
struct AudioSourceData;
struct AudioListenerData;

// Audio format enumeration
enum class AudioFormat {
    Unknown,
    WAV,
    MP3,
    OGG,
    FLAC
};

// Audio effect types
enum class AudioEffect {
    None,
    Reverb,
    Echo,
    Distortion
};

// Effect parameters
struct ReverbParams {
    float roomSize = 0.5f;      // 0.0 to 1.0
    float damping = 0.5f;       // 0.0 to 1.0
    float wetLevel = 0.3f;      // 0.0 to 1.0
    float dryLevel = 0.7f;      // 0.0 to 1.0
    float width = 1.0f;         // 0.0 to 1.0
};

struct EchoParams {
    float delayTime = 0.5f;     // seconds
    float feedback = 0.5f;      // 0.0 to 1.0
    float wetLevel = 0.3f;      // 0.0 to 1.0
    float dryLevel = 0.7f;      // 0.0 to 1.0
};

struct DistortionParams {
    float drive = 0.5f;         // 0.0 to 1.0
    float tone = 0.5f;          // 0.0 to 1.0
    float wetLevel = 0.5f;      // 0.0 to 1.0
    float dryLevel = 0.5f;      // 0.0 to 1.0
};

// Handle types for audio resources
using AudioSourceHandle = uint32_t;
using AudioClipHandle = uint32_t;
using MusicTrackHandle = uint32_t;

// Invalid handle constant
constexpr AudioSourceHandle INVALID_AUDIO_SOURCE = 0;
constexpr AudioClipHandle INVALID_AUDIO_CLIP = 0;
constexpr MusicTrackHandle INVALID_MUSIC_TRACK = 0;

// 3D position structure
struct Vec3 {
    float x, y, z;
    Vec3() : x(0), y(0), z(0) {}
    Vec3(float x, float y, float z) : x(x), y(y), z(z) {}
};

// Audio configuration
struct AudioConfig {
    int sampleRate = 44100;
    int channels = 2;
    int bufferSize = 4096;
    bool enableHRTF = true;
    float masterVolume = 1.0f;
};

// Audio clip data
struct AudioClip {
    std::string filePath;
    AudioFormat format;
    std::vector<uint8_t> data;
    int sampleRate;
    int channels;
    int bitsPerSample;
    float duration;
};

// Audio source properties
struct AudioSourceData {
    AudioClipHandle clipHandle;
    Vec3 position;
    Vec3 velocity;
    float volume;
    float pitch;
    bool looping;
    bool playing;
    bool paused;
    float currentTime;
    AudioEffect effect;
    ReverbParams reverbParams;
    EchoParams echoParams;
    DistortionParams distortionParams;
    
    AudioSourceData() 
        : clipHandle(INVALID_AUDIO_CLIP)
        , position()
        , velocity()
        , volume(1.0f)
        , pitch(1.0f)
        , looping(false)
        , playing(false)
        , paused(false)
        , currentTime(0.0f)
        , effect(AudioEffect::None)
        , reverbParams()
        , echoParams()
        , distortionParams()
    {}
};

// Audio listener properties
struct AudioListenerData {
    Vec3 position;
    Vec3 forward;
    Vec3 up;
    Vec3 velocity;
    
    AudioListenerData()
        : position()
        , forward(0, 0, -1)
        , up(0, 1, 0)
        , velocity()
    {}
};

// Game state enumeration for adaptive music
enum class GameState {
    Menu,
    Exploration,
    Combat,
    Puzzle,
    Cutscene,
    Victory,
    Defeat
};

// Music track data
struct MusicTrack {
    std::string name;
    AudioClipHandle clipHandle;
    GameState associatedState;
    float baseVolume;
    bool looping;
    
    MusicTrack()
        : name()
        , clipHandle(INVALID_AUDIO_CLIP)
        , associatedState(GameState::Menu)
        , baseVolume(1.0f)
        , looping(true)
    {}
};

// Music transition data
struct MusicTransition {
    MusicTrackHandle fromTrack;
    MusicTrackHandle toTrack;
    float duration;
    float currentTime;
    bool active;
    
    MusicTransition()
        : fromTrack(INVALID_MUSIC_TRACK)
        , toTrack(INVALID_MUSIC_TRACK)
        , duration(0.0f)
        , currentTime(0.0f)
        , active(false)
    {}
};

// Main AudioSystem class
class AudioSystem {
public:
    AudioSystem();
    ~AudioSystem();

    // Initialization and shutdown
    bool Initialize(const AudioConfig& config = AudioConfig());
    void Shutdown();
    bool IsInitialized() const { return initialized; }

    // Audio clip management
    AudioClipHandle LoadAudioClip(const std::string& filePath);
    void UnloadAudioClip(AudioClipHandle handle);
    bool IsClipValid(AudioClipHandle handle) const;
    AudioFormat DetectAudioFormat(const std::string& filePath) const;

    // Audio source management
    AudioSourceHandle CreateAudioSource(AudioClipHandle clipHandle);
    void DestroyAudioSource(AudioSourceHandle handle);
    bool IsSourceValid(AudioSourceHandle handle) const;

    // Playback control
    void Play(AudioSourceHandle source);
    void Pause(AudioSourceHandle source);
    void Stop(AudioSourceHandle source);
    bool IsPlaying(AudioSourceHandle source) const;
    bool IsPaused(AudioSourceHandle source) const;

    // 3D positional audio
    void SetSourcePosition(AudioSourceHandle source, const Vec3& position);
    Vec3 GetSourcePosition(AudioSourceHandle source) const;
    void SetSourceVelocity(AudioSourceHandle source, const Vec3& velocity);
    Vec3 GetSourceVelocity(AudioSourceHandle source) const;

    // Audio source properties
    void SetSourceVolume(AudioSourceHandle source, float volume);
    float GetSourceVolume(AudioSourceHandle source) const;
    void SetSourcePitch(AudioSourceHandle source, float pitch);
    float GetSourcePitch(AudioSourceHandle source) const;
    void SetSourceLooping(AudioSourceHandle source, bool looping);
    bool IsSourceLooping(AudioSourceHandle source) const;

    // Audio effects
    void SetSourceEffect(AudioSourceHandle source, AudioEffect effect);
    AudioEffect GetSourceEffect(AudioSourceHandle source) const;
    
    // Effect parameters
    void SetReverbParams(AudioSourceHandle source, const ReverbParams& params);
    ReverbParams GetReverbParams(AudioSourceHandle source) const;
    void SetEchoParams(AudioSourceHandle source, const EchoParams& params);
    EchoParams GetEchoParams(AudioSourceHandle source) const;
    void SetDistortionParams(AudioSourceHandle source, const DistortionParams& params);
    DistortionParams GetDistortionParams(AudioSourceHandle source) const;
    
    // Real-time parameter modulation
    void ModulateReverbRoomSize(AudioSourceHandle source, float roomSize);
    void ModulateEchoDelay(AudioSourceHandle source, float delayTime);
    void ModulateDistortionDrive(AudioSourceHandle source, float drive);

    // Listener management
    void SetListenerPosition(const Vec3& position);
    Vec3 GetListenerPosition() const;
    void SetListenerOrientation(const Vec3& forward, const Vec3& up);
    void GetListenerOrientation(Vec3& forward, Vec3& up) const;
    void SetListenerVelocity(const Vec3& velocity);
    Vec3 GetListenerVelocity() const;

    // HRTF processing
    void EnableHRTF(bool enable);
    bool IsHRTFEnabled() const;

    // Master controls
    void SetMasterVolume(float volume);
    float GetMasterVolume() const;
    
    // Adaptive music system
    MusicTrackHandle CreateMusicTrack(const std::string& name, AudioClipHandle clipHandle, GameState state);
    void DestroyMusicTrack(MusicTrackHandle handle);
    bool IsMusicTrackValid(MusicTrackHandle handle) const;
    
    void PlayAdaptiveMusic(MusicTrackHandle track, GameState currentState);
    void StopAdaptiveMusic();
    void CrossfadeMusic(MusicTrackHandle newTrack, float duration);
    
    void SetCurrentGameState(GameState state);
    GameState GetCurrentGameState() const;
    
    MusicTrackHandle GetCurrentMusicTrack() const;
    bool IsMusicPlaying() const;
    bool IsCrossfading() const;

    // Update (called per frame)
    void Update(float deltaTime);

private:
    bool initialized;
    AudioConfig config;
    AudioListenerData listener;
    
    // Resource storage
    std::unordered_map<AudioClipHandle, std::unique_ptr<AudioClip>> audioClips;
    std::unordered_map<AudioSourceHandle, std::unique_ptr<AudioSourceData>> audioSources;
    std::unordered_map<MusicTrackHandle, std::unique_ptr<MusicTrack>> musicTracks;
    
    // Handle generation
    AudioClipHandle nextClipHandle;
    AudioSourceHandle nextSourceHandle;
    MusicTrackHandle nextMusicTrackHandle;
    
    // Adaptive music state
    GameState currentGameState;
    MusicTrackHandle currentMusicTrack;
    AudioSourceHandle currentMusicSource;
    MusicTransition activeTransition;
    
    // Helper methods
    AudioClipHandle GenerateClipHandle();
    AudioSourceHandle GenerateSourceHandle();
    MusicTrackHandle GenerateMusicTrackHandle();
    bool LoadWAV(const std::string& filePath, AudioClip& clip);
    bool LoadMP3(const std::string& filePath, AudioClip& clip);
    bool LoadOGG(const std::string& filePath, AudioClip& clip);
    bool LoadFLAC(const std::string& filePath, AudioClip& clip);
    
    // 3D audio processing
    void ProcessHRTF(AudioSourceData& source, const AudioListenerData& listener);
    float CalculateAttenuation(const Vec3& sourcePos, const Vec3& listenerPos) const;
    void ApplyDopplerEffect(AudioSourceData& source, const AudioListenerData& listener);
    
    // Audio effect processing
    void ProcessAudioEffects(AudioSourceData& source, float deltaTime);
    void ApplyReverb(AudioSourceData& source);
    void ApplyEcho(AudioSourceData& source, float deltaTime);
    void ApplyDistortion(AudioSourceData& source);
    
    // Adaptive music processing
    void UpdateAdaptiveMusic(float deltaTime);
    void ProcessMusicTransition(float deltaTime);
};

} // namespace audio
} // namespace pywrkgame