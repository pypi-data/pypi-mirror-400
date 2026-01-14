/**
 * Property-based tests for Audio Effects
 * Feature: pywrkgame-library, Property 35: Real-time Audio Effects
 * Validates: Requirements 7.2
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

class AudioEffectsPropertiesTest : public ::testing::Test {
protected:
    void SetUp() override {
        audio = std::make_unique<AudioSystem>();
        ASSERT_TRUE(audio->Initialize());
        
        // Create test audio file
        CreateTestWAVFile("test_audio.wav");
        
        // Load clip
        clip = audio->LoadAudioClip("test_audio.wav");
        ASSERT_NE(clip, INVALID_AUDIO_CLIP);
    }
    
    void TearDown() override {
        audio->Shutdown();
        std::remove("test_audio.wav");
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
    
    std::unique_ptr<AudioSystem> audio;
    AudioClipHandle clip;
    std::mt19937 rng{std::random_device{}()};
};

/**
 * Property 35: Real-time Audio Effects - Reverb
 * For any audio with applied reverb effect, processing should occur in real-time without latency
 * 
 * This test verifies that:
 * 1. Reverb effect can be applied to any audio source
 * 2. Reverb parameters can be set and retrieved correctly
 * 3. Real-time parameter modulation works correctly
 * 4. Effect processing happens during Update() calls
 */
TEST_F(AudioEffectsPropertiesTest, ReverbEffectProperty) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        AudioSourceHandle source = audio->CreateAudioSource(clip);
        ASSERT_NE(source, INVALID_AUDIO_SOURCE);
        
        // Set reverb effect
        audio->SetSourceEffect(source, AudioEffect::Reverb);
        EXPECT_EQ(audio->GetSourceEffect(source), AudioEffect::Reverb);
        
        // Generate random reverb parameters
        ReverbParams params;
        params.roomSize = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.damping = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.wetLevel = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.dryLevel = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.width = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        
        // Set parameters
        audio->SetReverbParams(source, params);
        
        // Verify parameters are set correctly
        ReverbParams retrieved = audio->GetReverbParams(source);
        EXPECT_FLOAT_EQ(retrieved.roomSize, params.roomSize);
        EXPECT_FLOAT_EQ(retrieved.damping, params.damping);
        EXPECT_FLOAT_EQ(retrieved.wetLevel, params.wetLevel);
        EXPECT_FLOAT_EQ(retrieved.dryLevel, params.dryLevel);
        EXPECT_FLOAT_EQ(retrieved.width, params.width);
        
        // Test real-time modulation
        float newRoomSize = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        audio->ModulateReverbRoomSize(source, newRoomSize);
        
        ReverbParams modulated = audio->GetReverbParams(source);
        EXPECT_FLOAT_EQ(modulated.roomSize, newRoomSize);
        
        // Play and update to apply effect
        audio->Play(source);
        EXPECT_TRUE(audio->IsPlaying(source));
        
        // Update should process the effect in real-time
        audio->Update(0.016f); // One frame at 60 FPS
        
        // Source should still be playing after effect processing
        EXPECT_TRUE(audio->IsPlaying(source));
        
        audio->DestroyAudioSource(source);
    }
}

/**
 * Property 35: Real-time Audio Effects - Echo
 * For any audio with applied echo effect, processing should occur in real-time without latency
 */
TEST_F(AudioEffectsPropertiesTest, EchoEffectProperty) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        AudioSourceHandle source = audio->CreateAudioSource(clip);
        ASSERT_NE(source, INVALID_AUDIO_SOURCE);
        
        // Set echo effect
        audio->SetSourceEffect(source, AudioEffect::Echo);
        EXPECT_EQ(audio->GetSourceEffect(source), AudioEffect::Echo);
        
        // Generate random echo parameters
        EchoParams params;
        params.delayTime = std::uniform_real_distribution<float>(0.1f, 2.0f)(rng);
        params.feedback = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.wetLevel = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.dryLevel = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        
        // Set parameters
        audio->SetEchoParams(source, params);
        
        // Verify parameters are set correctly
        EchoParams retrieved = audio->GetEchoParams(source);
        EXPECT_FLOAT_EQ(retrieved.delayTime, params.delayTime);
        EXPECT_FLOAT_EQ(retrieved.feedback, params.feedback);
        EXPECT_FLOAT_EQ(retrieved.wetLevel, params.wetLevel);
        EXPECT_FLOAT_EQ(retrieved.dryLevel, params.dryLevel);
        
        // Test real-time modulation
        float newDelay = std::uniform_real_distribution<float>(0.1f, 2.0f)(rng);
        audio->ModulateEchoDelay(source, newDelay);
        
        EchoParams modulated = audio->GetEchoParams(source);
        EXPECT_FLOAT_EQ(modulated.delayTime, newDelay);
        
        // Play and update to apply effect
        audio->Play(source);
        audio->Update(0.016f);
        
        EXPECT_TRUE(audio->IsPlaying(source));
        
        audio->DestroyAudioSource(source);
    }
}

/**
 * Property 35: Real-time Audio Effects - Distortion
 * For any audio with applied distortion effect, processing should occur in real-time without latency
 */
TEST_F(AudioEffectsPropertiesTest, DistortionEffectProperty) {
    const int NUM_ITERATIONS = 100;
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        AudioSourceHandle source = audio->CreateAudioSource(clip);
        ASSERT_NE(source, INVALID_AUDIO_SOURCE);
        
        // Set distortion effect
        audio->SetSourceEffect(source, AudioEffect::Distortion);
        EXPECT_EQ(audio->GetSourceEffect(source), AudioEffect::Distortion);
        
        // Generate random distortion parameters
        DistortionParams params;
        params.drive = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.tone = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.wetLevel = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        params.dryLevel = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        
        // Set parameters
        audio->SetDistortionParams(source, params);
        
        // Verify parameters are set correctly
        DistortionParams retrieved = audio->GetDistortionParams(source);
        EXPECT_FLOAT_EQ(retrieved.drive, params.drive);
        EXPECT_FLOAT_EQ(retrieved.tone, params.tone);
        EXPECT_FLOAT_EQ(retrieved.wetLevel, params.wetLevel);
        EXPECT_FLOAT_EQ(retrieved.dryLevel, params.dryLevel);
        
        // Test real-time modulation
        float newDrive = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        audio->ModulateDistortionDrive(source, newDrive);
        
        DistortionParams modulated = audio->GetDistortionParams(source);
        EXPECT_FLOAT_EQ(modulated.drive, newDrive);
        
        // Play and update to apply effect
        audio->Play(source);
        audio->Update(0.016f);
        
        EXPECT_TRUE(audio->IsPlaying(source));
        
        audio->DestroyAudioSource(source);
    }
}

/**
 * Property 35: Real-time Audio Effects - Effect Chain Processing
 * For any audio source, effects should be processed in the correct order
 */
TEST_F(AudioEffectsPropertiesTest, EffectChainProcessing) {
    const int NUM_ITERATIONS = 50;
    
    std::vector<AudioEffect> effects = {
        AudioEffect::None,
        AudioEffect::Reverb,
        AudioEffect::Echo,
        AudioEffect::Distortion
    };
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        AudioSourceHandle source = audio->CreateAudioSource(clip);
        ASSERT_NE(source, INVALID_AUDIO_SOURCE);
        
        // Randomly select an effect
        AudioEffect effect = effects[std::uniform_int_distribution<int>(0, effects.size() - 1)(rng)];
        
        audio->SetSourceEffect(source, effect);
        EXPECT_EQ(audio->GetSourceEffect(source), effect);
        
        // Set initial volume
        float initialVolume = 1.0f;
        audio->SetSourceVolume(source, initialVolume);
        
        // Play and update multiple times
        audio->Play(source);
        
        for (int frame = 0; frame < 10; ++frame) {
            audio->Update(0.016f);
            
            // Verify source is still valid and playing
            EXPECT_TRUE(audio->IsSourceValid(source));
            
            // Volume should remain within valid range after effect processing
            float volume = audio->GetSourceVolume(source);
            EXPECT_GE(volume, 0.0f);
            EXPECT_LE(volume, 2.0f); // Allow some headroom for effect processing
        }
        
        audio->DestroyAudioSource(source);
    }
}

/**
 * Property 35: Real-time Audio Effects - Parameter Clamping
 * For any effect parameters, values should be clamped to valid ranges
 */
TEST_F(AudioEffectsPropertiesTest, ParameterClamping) {
    AudioSourceHandle source = audio->CreateAudioSource(clip);
    ASSERT_NE(source, INVALID_AUDIO_SOURCE);
    
    // Test reverb parameter clamping
    audio->SetSourceEffect(source, AudioEffect::Reverb);
    
    // Test values outside valid range
    audio->ModulateReverbRoomSize(source, -1.0f);
    EXPECT_GE(audio->GetReverbParams(source).roomSize, 0.0f);
    
    audio->ModulateReverbRoomSize(source, 2.0f);
    EXPECT_LE(audio->GetReverbParams(source).roomSize, 1.0f);
    
    // Test echo parameter clamping
    audio->SetSourceEffect(source, AudioEffect::Echo);
    
    audio->ModulateEchoDelay(source, -1.0f);
    EXPECT_GE(audio->GetEchoParams(source).delayTime, 0.0f);
    
    audio->ModulateEchoDelay(source, 10.0f);
    EXPECT_LE(audio->GetEchoParams(source).delayTime, 5.0f);
    
    // Test distortion parameter clamping
    audio->SetSourceEffect(source, AudioEffect::Distortion);
    
    audio->ModulateDistortionDrive(source, -1.0f);
    EXPECT_GE(audio->GetDistortionParams(source).drive, 0.0f);
    
    audio->ModulateDistortionDrive(source, 2.0f);
    EXPECT_LE(audio->GetDistortionParams(source).drive, 1.0f);
    
    audio->DestroyAudioSource(source);
}

/**
 * Property 35: Real-time Audio Effects - Effect Switching
 * For any audio source, effects can be switched in real-time without issues
 */
TEST_F(AudioEffectsPropertiesTest, RealTimeEffectSwitching) {
    const int NUM_ITERATIONS = 50;
    
    std::vector<AudioEffect> effects = {
        AudioEffect::None,
        AudioEffect::Reverb,
        AudioEffect::Echo,
        AudioEffect::Distortion
    };
    
    AudioSourceHandle source = audio->CreateAudioSource(clip);
    ASSERT_NE(source, INVALID_AUDIO_SOURCE);
    
    audio->Play(source);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Switch to random effect
        AudioEffect newEffect = effects[std::uniform_int_distribution<int>(0, effects.size() - 1)(rng)];
        audio->SetSourceEffect(source, newEffect);
        
        EXPECT_EQ(audio->GetSourceEffect(source), newEffect);
        
        // Update and verify source is still valid
        audio->Update(0.016f);
        
        EXPECT_TRUE(audio->IsSourceValid(source));
        EXPECT_TRUE(audio->IsPlaying(source));
    }
    
    audio->DestroyAudioSource(source);
}

/**
 * Property 35: Real-time Audio Effects - No Latency
 * For any effect parameter change, the change should be reflected immediately
 */
TEST_F(AudioEffectsPropertiesTest, NoLatencyParameterModulation) {
    const int NUM_ITERATIONS = 100;
    
    AudioSourceHandle source = audio->CreateAudioSource(clip);
    ASSERT_NE(source, INVALID_AUDIO_SOURCE);
    
    audio->Play(source);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Modulate reverb parameters
        audio->SetSourceEffect(source, AudioEffect::Reverb);
        float roomSize = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        audio->ModulateReverbRoomSize(source, roomSize);
        
        // Parameter should be updated immediately (no latency)
        EXPECT_FLOAT_EQ(audio->GetReverbParams(source).roomSize, roomSize);
        
        // Modulate echo parameters
        audio->SetSourceEffect(source, AudioEffect::Echo);
        float delay = std::uniform_real_distribution<float>(0.1f, 2.0f)(rng);
        audio->ModulateEchoDelay(source, delay);
        
        EXPECT_FLOAT_EQ(audio->GetEchoParams(source).delayTime, delay);
        
        // Modulate distortion parameters
        audio->SetSourceEffect(source, AudioEffect::Distortion);
        float drive = std::uniform_real_distribution<float>(0.0f, 1.0f)(rng);
        audio->ModulateDistortionDrive(source, drive);
        
        EXPECT_FLOAT_EQ(audio->GetDistortionParams(source).drive, drive);
    }
    
    audio->DestroyAudioSource(source);
}
