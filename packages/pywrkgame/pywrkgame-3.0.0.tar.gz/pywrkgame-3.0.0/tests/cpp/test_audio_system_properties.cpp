/**
 * Property-based tests for Audio System
 * Feature: pywrkgame-library, Property 34: 3D Positional Audio
 * Feature: pywrkgame-library, Property 16: Format Support (Audio)
 * Validates: Requirements 7.1, 7.5
 */

#include <gtest/gtest.h>
#include "pywrkgame/audio/AudioSystem.h"
#include <vector>
#include <random>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <cstring>

using namespace pywrkgame::audio;

class AudioSystemPropertiesTest : public ::testing::Test {
protected:
    void SetUp() override {
        audio = std::make_unique<AudioSystem>();
        AudioConfig config;
        config.enableHRTF = true;
        ASSERT_TRUE(audio->Initialize(config));
        
        // Create test audio files
        CreateTestWAVFile("test_audio.wav");
        CreateTestFile("test_audio.mp3", "MP3");
        CreateTestFile("test_audio.ogg", "OGG");
        CreateTestFile("test_audio.flac", "FLAC");
    }
    
    void TearDown() override {
        audio->Shutdown();
        
        // Clean up test files
        std::remove("test_audio.wav");
        std::remove("test_audio.mp3");
        std::remove("test_audio.ogg");
        std::remove("test_audio.flac");
    }
    
    void CreateTestWAVFile(const std::string& filename) {
        std::ofstream file(filename, std::ios::binary);
        
        // WAV header (44 bytes)
        char header[44] = {0};
        
        // RIFF header
        std::memcpy(header, "RIFF", 4);
        uint32_t fileSize = 36 + 1000;
        std::memcpy(header + 4, &fileSize, 4);
        std::memcpy(header + 8, "WAVE", 4);
        
        // fmt chunk
        std::memcpy(header + 12, "fmt ", 4);
        uint32_t fmtSize = 16;
        std::memcpy(header + 16, &fmtSize, 4);
        uint16_t audioFormat = 1; // PCM
        std::memcpy(header + 20, &audioFormat, 2);
        uint16_t channels = 2;
        std::memcpy(header + 22, &channels, 2);
        uint32_t sampleRate = 44100;
        std::memcpy(header + 24, &sampleRate, 4);
        uint32_t byteRate = sampleRate * channels * 2;
        std::memcpy(header + 28, &byteRate, 4);
        uint16_t blockAlign = channels * 2;
        std::memcpy(header + 32, &blockAlign, 2);
        uint16_t bitsPerSample = 16;
        std::memcpy(header + 34, &bitsPerSample, 2);
        
        // data chunk
        std::memcpy(header + 36, "data", 4);
        uint32_t dataSize = 1000;
        std::memcpy(header + 40, &dataSize, 4);
        
        file.write(header, 44);
        
        // Write some dummy audio data
        std::vector<char> data(1000, 0);
        file.write(data.data(), 1000);
    }
    
    void CreateTestFile(const std::string& filename, const std::string& type) {
        std::ofstream file(filename, std::ios::binary);
        std::vector<char> data(1000, 0);
        file.write(data.data(), 1000);
    }
    
    Vec3 GenerateRandomPosition(std::mt19937& rng, float minVal, float maxVal) {
        std::uniform_real_distribution<float> dist(minVal, maxVal);
        return Vec3(dist(rng), dist(rng), dist(rng));
    }
    
    float Distance(const Vec3& a, const Vec3& b) {
        float dx = a.x - b.x;
        float dy = a.y - b.y;
        float dz = a.z - b.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
    
    std::unique_ptr<AudioSystem> audio;
    std::mt19937 rng{std::random_device{}()};
};

/**
 * Property 34: 3D Positional Audio
 * For any audio source in 3D space, positional audio should correctly reflect
 * distance and direction with HRTF processing
 * 
 * This test verifies that:
 * 1. Audio sources can be positioned anywhere in 3D space
 * 2. Position retrieval returns the exact position that was set
 * 3. Distance affects volume attenuation correctly
 * 4. HRTF processing is applied when enabled
 */
TEST_F(AudioSystemPropertiesTest, ThreeDPositionalAudio) {
    const int NUM_ITERATIONS = 100;
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    ASSERT_NE(clip, INVALID_AUDIO_CLIP);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate random positions for source and listener
        Vec3 sourcePos = GenerateRandomPosition(rng, -100.0f, 100.0f);
        Vec3 listenerPos = GenerateRandomPosition(rng, -100.0f, 100.0f);
        
        // Create audio source
        AudioSourceHandle source = audio->CreateAudioSource(clip);
        ASSERT_NE(source, INVALID_AUDIO_SOURCE);
        
        // Set source position
        audio->SetSourcePosition(source, sourcePos);
        
        // Verify position is set correctly
        Vec3 retrievedPos = audio->GetSourcePosition(source);
        EXPECT_FLOAT_EQ(retrievedPos.x, sourcePos.x);
        EXPECT_FLOAT_EQ(retrievedPos.y, sourcePos.y);
        EXPECT_FLOAT_EQ(retrievedPos.z, sourcePos.z);
        
        // Set listener position
        audio->SetListenerPosition(listenerPos);
        Vec3 retrievedListenerPos = audio->GetListenerPosition();
        EXPECT_FLOAT_EQ(retrievedListenerPos.x, listenerPos.x);
        EXPECT_FLOAT_EQ(retrievedListenerPos.y, listenerPos.y);
        EXPECT_FLOAT_EQ(retrievedListenerPos.z, listenerPos.z);
        
        // Calculate expected distance
        float distance = Distance(sourcePos, listenerPos);
        
        // Set initial volume
        float initialVolume = 1.0f;
        audio->SetSourceVolume(source, initialVolume);
        
        // Play the source and update to apply HRTF
        audio->Play(source);
        audio->Update(0.016f); // One frame
        
        // Verify HRTF is enabled
        EXPECT_TRUE(audio->IsHRTFEnabled());
        
        // Volume should be affected by distance (attenuation)
        // For very close sources (distance < 1), volume should be near original
        // For far sources, volume should be reduced
        if (distance < 1.0f) {
            // Close sources should maintain most of their volume
            EXPECT_GE(audio->GetSourceVolume(source), 0.5f);
        } else if (distance > 50.0f) {
            // Far sources should have significantly reduced volume
            EXPECT_LE(audio->GetSourceVolume(source), 0.1f);
        }
        
        audio->DestroyAudioSource(source);
    }
}

/**
 * Property 34: 3D Positional Audio - Velocity and Doppler Effect
 * For any audio source with velocity, the Doppler effect should be applied correctly
 */
TEST_F(AudioSystemPropertiesTest, DopplerEffectProperty) {
    const int NUM_ITERATIONS = 100;
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    ASSERT_NE(clip, INVALID_AUDIO_CLIP);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        AudioSourceHandle source = audio->CreateAudioSource(clip);
        ASSERT_NE(source, INVALID_AUDIO_SOURCE);
        
        // Generate random velocities
        Vec3 sourceVel = GenerateRandomPosition(rng, -50.0f, 50.0f);
        Vec3 listenerVel = GenerateRandomPosition(rng, -50.0f, 50.0f);
        
        // Set velocities
        audio->SetSourceVelocity(source, sourceVel);
        audio->SetListenerVelocity(listenerVel);
        
        // Verify velocities are set correctly
        Vec3 retrievedSourceVel = audio->GetSourceVelocity(source);
        EXPECT_FLOAT_EQ(retrievedSourceVel.x, sourceVel.x);
        EXPECT_FLOAT_EQ(retrievedSourceVel.y, sourceVel.y);
        EXPECT_FLOAT_EQ(retrievedSourceVel.z, sourceVel.z);
        
        Vec3 retrievedListenerVel = audio->GetListenerVelocity();
        EXPECT_FLOAT_EQ(retrievedListenerVel.x, listenerVel.x);
        EXPECT_FLOAT_EQ(retrievedListenerVel.y, listenerVel.y);
        EXPECT_FLOAT_EQ(retrievedListenerVel.z, listenerVel.z);
        
        // Set initial pitch
        float initialPitch = 1.0f;
        audio->SetSourcePitch(source, initialPitch);
        
        // Play and update to apply Doppler effect
        audio->Play(source);
        audio->Update(0.016f);
        
        // Pitch should be modified by Doppler effect
        // The exact value depends on relative velocity, but it should be within reasonable bounds
        float finalPitch = audio->GetSourcePitch(source);
        EXPECT_GE(finalPitch, 0.5f);
        EXPECT_LE(finalPitch, 2.0f);
        
        audio->DestroyAudioSource(source);
    }
}

/**
 * Property 16: Format Support (Audio)
 * For any supported audio format (MP3, OGG, WAV, FLAC), files should load correctly
 * 
 * This test verifies that:
 * 1. All supported formats can be detected correctly
 * 2. All supported formats can be loaded
 * 3. Audio sources can be created from clips of any format
 */
TEST_F(AudioSystemPropertiesTest, AudioFormatSupport) {
    std::vector<std::string> testFiles = {
        "test_audio.wav",
        "test_audio.mp3",
        "test_audio.ogg",
        "test_audio.flac"
    };
    
    std::vector<AudioFormat> expectedFormats = {
        AudioFormat::WAV,
        AudioFormat::MP3,
        AudioFormat::OGG,
        AudioFormat::FLAC
    };
    
    for (size_t i = 0; i < testFiles.size(); ++i) {
        const std::string& file = testFiles[i];
        AudioFormat expectedFormat = expectedFormats[i];
        
        // Verify format detection
        AudioFormat detectedFormat = audio->DetectAudioFormat(file);
        EXPECT_EQ(detectedFormat, expectedFormat) 
            << "Failed to detect format for " << file;
        
        // Verify file can be loaded
        AudioClipHandle clip = audio->LoadAudioClip(file);
        EXPECT_NE(clip, INVALID_AUDIO_CLIP) 
            << "Failed to load " << file;
        EXPECT_TRUE(audio->IsClipValid(clip))
            << "Clip is not valid for " << file;
        
        // Verify audio source can be created from this clip
        AudioSourceHandle source = audio->CreateAudioSource(clip);
        EXPECT_NE(source, INVALID_AUDIO_SOURCE)
            << "Failed to create source for " << file;
        EXPECT_TRUE(audio->IsSourceValid(source))
            << "Source is not valid for " << file;
        
        // Verify playback control works
        audio->Play(source);
        EXPECT_TRUE(audio->IsPlaying(source))
            << "Failed to play " << file;
        
        audio->Stop(source);
        EXPECT_FALSE(audio->IsPlaying(source))
            << "Failed to stop " << file;
        
        // Clean up
        audio->DestroyAudioSource(source);
        audio->UnloadAudioClip(clip);
    }
}

/**
 * Property 34: 3D Positional Audio - Listener Orientation
 * For any listener orientation, the audio system should correctly track forward and up vectors
 */
TEST_F(AudioSystemPropertiesTest, ListenerOrientationProperty) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Generate random normalized forward and up vectors
        Vec3 forward = GenerateRandomPosition(rng, -1.0f, 1.0f);
        Vec3 up = GenerateRandomPosition(rng, -1.0f, 1.0f);
        
        // Normalize vectors
        float forwardLen = std::sqrt(forward.x * forward.x + forward.y * forward.y + forward.z * forward.z);
        float upLen = std::sqrt(up.x * up.x + up.y * up.y + up.z * up.z);
        
        if (forwardLen > 0.001f) {
            forward.x /= forwardLen;
            forward.y /= forwardLen;
            forward.z /= forwardLen;
        }
        
        if (upLen > 0.001f) {
            up.x /= upLen;
            up.y /= upLen;
            up.z /= upLen;
        }
        
        // Set listener orientation
        audio->SetListenerOrientation(forward, up);
        
        // Retrieve and verify
        Vec3 retrievedForward, retrievedUp;
        audio->GetListenerOrientation(retrievedForward, retrievedUp);
        
        EXPECT_NEAR(retrievedForward.x, forward.x, 0.001f);
        EXPECT_NEAR(retrievedForward.y, forward.y, 0.001f);
        EXPECT_NEAR(retrievedForward.z, forward.z, 0.001f);
        
        EXPECT_NEAR(retrievedUp.x, up.x, 0.001f);
        EXPECT_NEAR(retrievedUp.y, up.y, 0.001f);
        EXPECT_NEAR(retrievedUp.z, up.z, 0.001f);
    }
}

/**
 * Property 34: 3D Positional Audio - Volume Attenuation
 * For any two positions, closer sources should be louder than farther sources
 */
TEST_F(AudioSystemPropertiesTest, VolumeAttenuationProperty) {
    const int NUM_ITERATIONS = 50;
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    ASSERT_NE(clip, INVALID_AUDIO_CLIP);
    
    Vec3 listenerPos(0.0f, 0.0f, 0.0f);
    audio->SetListenerPosition(listenerPos);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Create two sources at different distances
        float nearDistance = std::uniform_real_distribution<float>(1.0f, 10.0f)(rng);
        float farDistance = std::uniform_real_distribution<float>(20.0f, 50.0f)(rng);
        
        Vec3 nearPos(nearDistance, 0.0f, 0.0f);
        Vec3 farPos(farDistance, 0.0f, 0.0f);
        
        AudioSourceHandle nearSource = audio->CreateAudioSource(clip);
        AudioSourceHandle farSource = audio->CreateAudioSource(clip);
        
        audio->SetSourcePosition(nearSource, nearPos);
        audio->SetSourcePosition(farSource, farPos);
        
        audio->SetSourceVolume(nearSource, 1.0f);
        audio->SetSourceVolume(farSource, 1.0f);
        
        audio->Play(nearSource);
        audio->Play(farSource);
        
        audio->Update(0.016f);
        
        // Near source should have higher volume than far source after attenuation
        float nearVolume = audio->GetSourceVolume(nearSource);
        float farVolume = audio->GetSourceVolume(farSource);
        
        EXPECT_GT(nearVolume, farVolume)
            << "Near source (distance=" << nearDistance << ") should be louder than far source (distance=" << farDistance << ")";
        
        audio->DestroyAudioSource(nearSource);
        audio->DestroyAudioSource(farSource);
    }
}

/**
 * Property 16: Format Support - Unknown Format Handling
 * For any file with unknown extension, the system should handle it gracefully
 */
TEST_F(AudioSystemPropertiesTest, UnknownFormatHandling) {
    std::vector<std::string> unknownFiles = {
        "test.txt",
        "test.xyz",
        "test.unknown",
        "test",
        "test."
    };
    
    for (const auto& file : unknownFiles) {
        AudioFormat format = audio->DetectAudioFormat(file);
        EXPECT_EQ(format, AudioFormat::Unknown)
            << "Should detect unknown format for " << file;
        
        // Attempting to load should fail gracefully
        AudioClipHandle clip = audio->LoadAudioClip(file);
        EXPECT_EQ(clip, INVALID_AUDIO_CLIP)
            << "Should not load unknown format " << file;
    }
}
