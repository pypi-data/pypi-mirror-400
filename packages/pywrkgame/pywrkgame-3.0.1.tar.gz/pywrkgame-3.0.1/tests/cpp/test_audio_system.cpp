#include <gtest/gtest.h>
#include "pywrkgame/audio/AudioSystem.h"
#include <fstream>
#include <cstring>

using namespace pywrkgame::audio;

class AudioSystemTest : public ::testing::Test {
protected:
    void SetUp() override {
        audio = std::make_unique<AudioSystem>();
        
        // Create a simple test WAV file
        CreateTestWAVFile("test_audio.wav");
    }
    
    void TearDown() override {
        // Clean up test files
        std::remove("test_audio.wav");
    }
    
    void CreateTestWAVFile(const std::string& filename) {
        std::ofstream file(filename, std::ios::binary);
        
        // WAV header (44 bytes)
        char header[44] = {0};
        
        // RIFF header
        std::memcpy(header, "RIFF", 4);
        uint32_t fileSize = 36 + 1000; // header + data
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
};

TEST_F(AudioSystemTest, InitializeAndShutdown) {
    EXPECT_TRUE(audio->Initialize());
    EXPECT_TRUE(audio->IsInitialized());
    audio->Shutdown();
    EXPECT_FALSE(audio->IsInitialized());
}

TEST_F(AudioSystemTest, LoadAudioClip) {
    ASSERT_TRUE(audio->Initialize());
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    EXPECT_NE(clip, INVALID_AUDIO_CLIP);
    EXPECT_TRUE(audio->IsClipValid(clip));
    
    audio->UnloadAudioClip(clip);
    EXPECT_FALSE(audio->IsClipValid(clip));
}

TEST_F(AudioSystemTest, DetectAudioFormat) {
    ASSERT_TRUE(audio->Initialize());
    
    EXPECT_EQ(audio->DetectAudioFormat("test.wav"), AudioFormat::WAV);
    EXPECT_EQ(audio->DetectAudioFormat("test.mp3"), AudioFormat::MP3);
    EXPECT_EQ(audio->DetectAudioFormat("test.ogg"), AudioFormat::OGG);
    EXPECT_EQ(audio->DetectAudioFormat("test.flac"), AudioFormat::FLAC);
    EXPECT_EQ(audio->DetectAudioFormat("test.unknown"), AudioFormat::Unknown);
}

TEST_F(AudioSystemTest, CreateAudioSource) {
    ASSERT_TRUE(audio->Initialize());
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    ASSERT_NE(clip, INVALID_AUDIO_CLIP);
    
    AudioSourceHandle source = audio->CreateAudioSource(clip);
    EXPECT_NE(source, INVALID_AUDIO_SOURCE);
    EXPECT_TRUE(audio->IsSourceValid(source));
    
    audio->DestroyAudioSource(source);
    EXPECT_FALSE(audio->IsSourceValid(source));
}

TEST_F(AudioSystemTest, PlaybackControl) {
    ASSERT_TRUE(audio->Initialize());
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    AudioSourceHandle source = audio->CreateAudioSource(clip);
    
    EXPECT_FALSE(audio->IsPlaying(source));
    
    audio->Play(source);
    EXPECT_TRUE(audio->IsPlaying(source));
    EXPECT_FALSE(audio->IsPaused(source));
    
    audio->Pause(source);
    EXPECT_FALSE(audio->IsPlaying(source));
    EXPECT_TRUE(audio->IsPaused(source));
    
    audio->Stop(source);
    EXPECT_FALSE(audio->IsPlaying(source));
    EXPECT_FALSE(audio->IsPaused(source));
}

TEST_F(AudioSystemTest, PositionalAudio) {
    ASSERT_TRUE(audio->Initialize());
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    AudioSourceHandle source = audio->CreateAudioSource(clip);
    
    Vec3 position(10.0f, 5.0f, -3.0f);
    audio->SetSourcePosition(source, position);
    
    Vec3 retrieved = audio->GetSourcePosition(source);
    EXPECT_FLOAT_EQ(retrieved.x, position.x);
    EXPECT_FLOAT_EQ(retrieved.y, position.y);
    EXPECT_FLOAT_EQ(retrieved.z, position.z);
}

TEST_F(AudioSystemTest, SourceProperties) {
    ASSERT_TRUE(audio->Initialize());
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    AudioSourceHandle source = audio->CreateAudioSource(clip);
    
    // Test volume
    audio->SetSourceVolume(source, 0.5f);
    EXPECT_FLOAT_EQ(audio->GetSourceVolume(source), 0.5f);
    
    // Test pitch
    audio->SetSourcePitch(source, 1.5f);
    EXPECT_FLOAT_EQ(audio->GetSourcePitch(source), 1.5f);
    
    // Test looping
    audio->SetSourceLooping(source, true);
    EXPECT_TRUE(audio->IsSourceLooping(source));
}

TEST_F(AudioSystemTest, ListenerManagement) {
    ASSERT_TRUE(audio->Initialize());
    
    Vec3 position(1.0f, 2.0f, 3.0f);
    audio->SetListenerPosition(position);
    
    Vec3 retrieved = audio->GetListenerPosition();
    EXPECT_FLOAT_EQ(retrieved.x, position.x);
    EXPECT_FLOAT_EQ(retrieved.y, position.y);
    EXPECT_FLOAT_EQ(retrieved.z, position.z);
    
    Vec3 forward(0.0f, 0.0f, -1.0f);
    Vec3 up(0.0f, 1.0f, 0.0f);
    audio->SetListenerOrientation(forward, up);
    
    Vec3 retrievedForward, retrievedUp;
    audio->GetListenerOrientation(retrievedForward, retrievedUp);
    EXPECT_FLOAT_EQ(retrievedForward.z, -1.0f);
    EXPECT_FLOAT_EQ(retrievedUp.y, 1.0f);
}

TEST_F(AudioSystemTest, HRTFControl) {
    ASSERT_TRUE(audio->Initialize());
    
    audio->EnableHRTF(true);
    EXPECT_TRUE(audio->IsHRTFEnabled());
    
    audio->EnableHRTF(false);
    EXPECT_FALSE(audio->IsHRTFEnabled());
}

TEST_F(AudioSystemTest, MasterVolume) {
    ASSERT_TRUE(audio->Initialize());
    
    audio->SetMasterVolume(0.7f);
    EXPECT_FLOAT_EQ(audio->GetMasterVolume(), 0.7f);
}

TEST_F(AudioSystemTest, AudioEffects) {
    ASSERT_TRUE(audio->Initialize());
    
    AudioClipHandle clip = audio->LoadAudioClip("test_audio.wav");
    AudioSourceHandle source = audio->CreateAudioSource(clip);
    
    audio->SetSourceEffect(source, AudioEffect::Reverb);
    EXPECT_EQ(audio->GetSourceEffect(source), AudioEffect::Reverb);
    
    audio->SetSourceEffect(source, AudioEffect::Echo);
    EXPECT_EQ(audio->GetSourceEffect(source), AudioEffect::Echo);
}