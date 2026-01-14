#include <gtest/gtest.h>
#include "pywrkgame/core/EngineCore.h"
#include "pywrkgame/platform/PlatformManager.h"

using namespace pywrkgame::core;
using namespace pywrkgame::platform;

class EngineCoreTest : public ::testing::Test {
protected:
    void SetUp() override {
        engine = std::make_unique<EngineCore>();
    }
    
    void TearDown() override {
        if (engine && engine->IsInitialized()) {
            engine->Shutdown();
        }
    }
    
    std::unique_ptr<EngineCore> engine;
    EngineConfig config;
};

TEST_F(EngineCoreTest, InitializeAndShutdown) {
    EXPECT_FALSE(engine->IsInitialized());
    
    EXPECT_TRUE(engine->Initialize(config));
    EXPECT_TRUE(engine->IsInitialized());
    
    engine->Shutdown();
    EXPECT_FALSE(engine->IsInitialized());
}

TEST_F(EngineCoreTest, DoubleInitializationFails) {
    EXPECT_TRUE(engine->Initialize(config));
    EXPECT_FALSE(engine->Initialize(config)); // Second initialization should fail
}

TEST_F(EngineCoreTest, UpdateWithoutInitialization) {
    // Should not crash when calling update without initialization
    EXPECT_NO_THROW(engine->Update(0.016f));
}

TEST_F(EngineCoreTest, RenderWithoutInitialization) {
    // Should not crash when calling render without initialization
    EXPECT_NO_THROW(engine->Render());
}

TEST_F(EngineCoreTest, GetSubsystemsAfterInitialization) {
    EXPECT_TRUE(engine->Initialize(config));
    
    // Should be able to get all subsystems after initialization
    EXPECT_NO_THROW(auto& entityManager = engine->GetEntityManager());
    EXPECT_NO_THROW(auto& systemManager = engine->GetSystemManager());
    EXPECT_NO_THROW(auto& componentManager = engine->GetComponentManager());
    EXPECT_NO_THROW(auto& renderer = engine->GetRenderer());
    EXPECT_NO_THROW(auto& physics = engine->GetPhysics());
    EXPECT_NO_THROW(auto& audio = engine->GetAudio());
    EXPECT_NO_THROW(auto& network = engine->GetNetwork());
}