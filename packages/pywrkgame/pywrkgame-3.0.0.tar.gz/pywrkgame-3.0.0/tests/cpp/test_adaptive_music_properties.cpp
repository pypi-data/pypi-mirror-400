/**
 * Property-based tests for Adaptive Music System
 * Feature: pywrkgame-library, Property 36: Adaptive Music System
 * Validates: Requirements 7.3
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

class AdaptiveMusicPropertiesTest : public ::testing::Test {
protected:
    void SetUp() override {
        audio = std::make_unique<AudioSystem>();
        ASSERT_TRUE(audio->Initialize());
        
        // Create test audio files for different game states
        CreateTestWAVFile("menu_music.wav");
        CreateTestWAVFile("exploration_music.wav");
        CreateTestWAVFile("combat_music.wav");
        CreateTestWAVFile("victory_music.wav");
        
        // Load clips
        menuClip = audio->LoadAudioClip("menu_music.wav");
        explorationClip = audio->LoadAudioClip("exploration_music.wav");
        combatClip = audio->LoadAudioClip("combat_music.wav");
        victoryClip = audio->LoadAudioClip("victory_music.wav");
        
        ASSERT_NE(menuClip, INVALID_AUDIO_CLIP);
        ASSERT_NE(explorationClip, INVALID_AUDIO_CLIP);
        ASSERT_NE(combatClip, INVALID_AUDIO_CLIP);
        ASSERT_NE(victoryClip, INVALID_AUDIO_CLIP);
    }
    
    void TearDown() override {
        audio->Shutdown();
        
        std::remove("menu_music.wav");
        std::remove("exploration_music.wav");
        std::remove("combat_music.wav");
        std::remove("victory_music.wav");
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
    AudioClipHandle menuClip;
    AudioClipHandle explorationClip;
    AudioClipHandle combatClip;
    AudioClipHandle victoryClip;
    std::mt19937 rng{std::random_device{}()};
};

/**
 * Property 36: Adaptive Music System - State-based Music Switching
 * For any game state change, adaptive music should transition appropriately to match the new context
 * 
 * This test verifies that:
 * 1. Music tracks can be created and associated with game states
 * 2. Music automatically switches when game state changes
 * 3. Music tracks are valid and can be played
 */
TEST_F(AdaptiveMusicPropertiesTest, StateBased MusicSwitching) {
    // Create music tracks for different game states
    MusicTrackHandle menuTrack = audio->CreateMusicTrack("Menu Music", menuClip, GameState::Menu);
    MusicTrackHandle explorationTrack = audio->CreateMusicTrack("Exploration Music", explorationClip, GameState::Exploration);
    MusicTrackHandle combatTrack = audio->CreateMusicTrack("Combat Music", combatClip, GameState::Combat);
    MusicTrackHandle victoryTrack = audio->CreateMusicTrack("Victory Music", victoryClip, GameState::Victory);
    
    ASSERT_NE(menuTrack, INVALID_MUSIC_TRACK);
    ASSERT_NE(explorationTrack, INVALID_MUSIC_TRACK);
    ASSERT_NE(combatTrack, INVALID_MUSIC_TRACK);
    ASSERT_NE(victoryTrack, INVALID_MUSIC_TRACK);
    
    EXPECT_TRUE(audio->IsMusicTrackValid(menuTrack));
    EXPECT_TRUE(audio->IsMusicTrackValid(explorationTrack));
    EXPECT_TRUE(audio->IsMusicTrackValid(combatTrack));
    EXPECT_TRUE(audio->IsMusicTrackValid(victoryTrack));
    
    // Test state transitions
    std::vector<GameState> states = {
        GameState::Menu,
        GameState::Exploration,
        GameState::Combat,
        GameState::Victory
    };
    
    std::vector<MusicTrackHandle> tracks = {
        menuTrack,
        explorationTrack,
        combatTrack,
        victoryTrack
    };
    
    for (size_t i = 0; i < states.size(); ++i) {
        GameState state = states[i];
        MusicTrackHandle expectedTrack = tracks[i];
        
        // Set game state (should automatically switch music)
        audio->SetCurrentGameState(state);
        
        // Verify state is set
        EXPECT_EQ(audio->GetCurrentGameState(), state);
        
        // Update to process music transition
        for (int frame = 0; frame < 10; ++frame) {
            audio->Update(0.016f);
        }
        
        // Verify correct track is playing
        EXPECT_EQ(audio->GetCurrentMusicTrack(), expectedTrack);
        EXPECT_TRUE(audio->IsMusicPlaying());
    }
}

/**
 * Property 36: Adaptive Music System - Crossfading
 * For any music transition, crossfading should work smoothly with specified duration
 */
TEST_F(AdaptiveMusicPropertiesTest, CrossfadingProperty) {
    const int NUM_ITERATIONS = 50;
    
    // Create two music tracks
    MusicTrackHandle track1 = audio->CreateMusicTrack("Track 1", menuClip, GameState::Menu);
    MusicTrackHandle track2 = audio->CreateMusicTrack("Track 2", explorationClip, GameState::Exploration);
    
    ASSERT_NE(track1, INVALID_MUSIC_TRACK);
    ASSERT_NE(track2, INVALID_MUSIC_TRACK);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        // Start with first track
        audio->PlayAdaptiveMusic(track1, GameState::Menu);
        EXPECT_TRUE(audio->IsMusicPlaying());
        EXPECT_EQ(audio->GetCurrentMusicTrack(), track1);
        
        // Generate random crossfade duration
        float duration = std::uniform_real_distribution<float>(0.5f, 3.0f)(rng);
        
        // Crossfade to second track
        audio->CrossfadeMusic(track2, duration);
        
        // Verify crossfade is active
        EXPECT_TRUE(audio->IsCrossfading());
        
        // Simulate crossfade by updating over the duration
        float elapsed = 0.0f;
        const float frameTime = 0.016f;
        
        while (elapsed < duration + frameTime) {
            audio->Update(frameTime);
            elapsed += frameTime;
        }
        
        // After crossfade completes, should be playing track2
        EXPECT_EQ(audio->GetCurrentMusicTrack(), track2);
        EXPECT_TRUE(audio->IsMusicPlaying());
        EXPECT_FALSE(audio->IsCrossfading());
        
        // Crossfade back to track1
        audio->CrossfadeMusic(track1, duration);
        
        elapsed = 0.0f;
        while (elapsed < duration + frameTime) {
            audio->Update(frameTime);
            elapsed += frameTime;
        }
        
        EXPECT_EQ(audio->GetCurrentMusicTrack(), track1);
    }
}

/**
 * Property 36: Adaptive Music System - Music State Management
 * For any music track, state management should work correctly
 */
TEST_F(AdaptiveMusicPropertiesTest, MusicStateManagement) {
    MusicTrackHandle track = audio->CreateMusicTrack("Test Track", menuClip, GameState::Menu);
    ASSERT_NE(track, INVALID_MUSIC_TRACK);
    
    // Initially no music should be playing
    EXPECT_FALSE(audio->IsMusicPlaying());
    EXPECT_EQ(audio->GetCurrentMusicTrack(), INVALID_MUSIC_TRACK);
    
    // Play music
    audio->PlayAdaptiveMusic(track, GameState::Menu);
    EXPECT_TRUE(audio->IsMusicPlaying());
    EXPECT_EQ(audio->GetCurrentMusicTrack(), track);
    
    // Stop music
    audio->StopAdaptiveMusic();
    EXPECT_FALSE(audio->IsMusicPlaying());
    EXPECT_EQ(audio->GetCurrentMusicTrack(), INVALID_MUSIC_TRACK);
    
    // Play again
    audio->PlayAdaptiveMusic(track, GameState::Menu);
    EXPECT_TRUE(audio->IsMusicPlaying());
    
    // Destroy track while playing
    audio->DestroyMusicTrack(track);
    EXPECT_FALSE(audio->IsMusicPlaying());
    EXPECT_FALSE(audio->IsMusicTrackValid(track));
}

/**
 * Property 36: Adaptive Music System - Multiple State Transitions
 * For any sequence of game state changes, music should adapt correctly
 */
TEST_F(AdaptiveMusicPropertiesTest, MultipleStateTransitions) {
    // Create tracks for all states
    std::vector<GameState> states = {
        GameState::Menu,
        GameState::Exploration,
        GameState::Combat,
        GameState::Puzzle,
        GameState::Cutscene,
        GameState::Victory,
        GameState::Defeat
    };
    
    std::vector<AudioClipHandle> clips = {
        menuClip,
        explorationClip,
        combatClip,
        menuClip,  // Reuse for puzzle
        explorationClip,  // Reuse for cutscene
        victoryClip,
        combatClip  // Reuse for defeat
    };
    
    std::vector<MusicTrackHandle> tracks;
    for (size_t i = 0; i < states.size(); ++i) {
        MusicTrackHandle track = audio->CreateMusicTrack(
            "Track " + std::to_string(i),
            clips[i],
            states[i]
        );
        ASSERT_NE(track, INVALID_MUSIC_TRACK);
        tracks.push_back(track);
    }
    
    // Perform random state transitions
    const int NUM_TRANSITIONS = 100;
    for (int i = 0; i < NUM_TRANSITIONS; ++i) {
        int stateIndex = std::uniform_int_distribution<int>(0, states.size() - 1)(rng);
        GameState newState = states[stateIndex];
        
        audio->SetCurrentGameState(newState);
        
        // Update to process transition
        for (int frame = 0; frame < 5; ++frame) {
            audio->Update(0.016f);
        }
        
        // Verify state is correct
        EXPECT_EQ(audio->GetCurrentGameState(), newState);
        
        // Music should be playing
        EXPECT_TRUE(audio->IsMusicPlaying());
    }
}

/**
 * Property 36: Adaptive Music System - Crossfade Duration Accuracy
 * For any crossfade duration, the transition should complete in approximately that time
 */
TEST_F(AdaptiveMusicPropertiesTest, CrossfadeDurationAccuracy) {
    const int NUM_ITERATIONS = 50;
    
    MusicTrackHandle track1 = audio->CreateMusicTrack("Track 1", menuClip, GameState::Menu);
    MusicTrackHandle track2 = audio->CreateMusicTrack("Track 2", explorationClip, GameState::Exploration);
    
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        audio->PlayAdaptiveMusic(track1, GameState::Menu);
        
        float duration = std::uniform_real_distribution<float>(0.5f, 3.0f)(rng);
        audio->CrossfadeMusic(track2, duration);
        
        EXPECT_TRUE(audio->IsCrossfading());
        
        // Count frames until crossfade completes
        float elapsed = 0.0f;
        const float frameTime = 0.016f;
        int frameCount = 0;
        
        while (audio->IsCrossfading() && frameCount < 1000) {
            audio->Update(frameTime);
            elapsed += frameTime;
            frameCount++;
        }
        
        // Crossfade should complete within reasonable tolerance
        EXPECT_FALSE(audio->IsCrossfading());
        EXPECT_NEAR(elapsed, duration, 0.1f);  // 100ms tolerance
    }
}

/**
 * Property 36: Adaptive Music System - Gameplay-based Adaptation
 * For any gameplay context change, music should adapt appropriately
 */
TEST_F(AdaptiveMusicPropertiesTest, GameplayBasedAdaptation) {
    // Create tracks for gameplay scenarios
    MusicTrackHandle calmTrack = audio->CreateMusicTrack("Calm", explorationClip, GameState::Exploration);
    MusicTrackHandle intenseTrack = audio->CreateMusicTrack("Intense", combatClip, GameState::Combat);
    
    // Start in calm state
    audio->PlayAdaptiveMusic(calmTrack, GameState::Exploration);
    EXPECT_EQ(audio->GetCurrentGameState(), GameState::Exploration);
    EXPECT_TRUE(audio->IsMusicPlaying());
    
    // Simulate entering combat
    audio->SetCurrentGameState(GameState::Combat);
    
    // Update to process transition
    for (int i = 0; i < 150; ++i) {  // ~2.4 seconds at 60 FPS
        audio->Update(0.016f);
    }
    
    // Should now be playing combat music
    EXPECT_EQ(audio->GetCurrentGameState(), GameState::Combat);
    EXPECT_EQ(audio->GetCurrentMusicTrack(), intenseTrack);
    EXPECT_TRUE(audio->IsMusicPlaying());
    
    // Simulate leaving combat
    audio->SetCurrentGameState(GameState::Exploration);
    
    for (int i = 0; i < 150; ++i) {
        audio->Update(0.016f);
    }
    
    // Should return to calm music
    EXPECT_EQ(audio->GetCurrentGameState(), GameState::Exploration);
    EXPECT_EQ(audio->GetCurrentMusicTrack(), calmTrack);
    EXPECT_TRUE(audio->IsMusicPlaying());
}

/**
 * Property 36: Adaptive Music System - Track Reuse
 * For any music track, playing the same track multiple times should work correctly
 */
TEST_F(AdaptiveMusicPropertiesTest, TrackReuseProperty) {
    MusicTrackHandle track = audio->CreateMusicTrack("Reusable Track", menuClip, GameState::Menu);
    
    const int NUM_PLAYS = 50;
    for (int i = 0; i < NUM_PLAYS; ++i) {
        // Play the track
        audio->PlayAdaptiveMusic(track, GameState::Menu);
        EXPECT_TRUE(audio->IsMusicPlaying());
        EXPECT_EQ(audio->GetCurrentMusicTrack(), track);
        
        // Update for a few frames
        for (int frame = 0; frame < 10; ++frame) {
            audio->Update(0.016f);
        }
        
        // Stop the track
        audio->StopAdaptiveMusic();
        EXPECT_FALSE(audio->IsMusicPlaying());
        
        // Track should still be valid
        EXPECT_TRUE(audio->IsMusicTrackValid(track));
    }
}
