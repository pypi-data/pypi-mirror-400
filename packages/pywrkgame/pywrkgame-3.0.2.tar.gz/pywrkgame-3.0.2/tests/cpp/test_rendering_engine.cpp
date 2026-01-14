/**
 * Unit tests for Rendering Engine
 * Tests resource creation and management, basic rendering pipeline functionality
 * Validates: Requirements 3.1, 3.8
 */

#include <gtest/gtest.h>
#include "pywrkgame/rendering/RenderingEngine.h"
#include <vector>

using namespace pywrkgame::rendering;

class RenderingEngineTest : public ::testing::Test {
protected:
    void SetUp() override {
        renderer = std::make_unique<RenderingEngine>();
    }
    
    void TearDown() override {
        // Cleanup handled by destructor
    }
    
    std::unique_ptr<RenderingEngine> renderer;
};

// Basic initialization and shutdown tests
TEST_F(RenderingEngineTest, InitializeAndShutdown) {
    EXPECT_TRUE(renderer->Initialize());
    EXPECT_TRUE(renderer->IsInitialized());
    
    renderer->Shutdown();
    EXPECT_FALSE(renderer->IsInitialized());
}

TEST_F(RenderingEngineTest, DoubleInitializationFails) {
    EXPECT_TRUE(renderer->Initialize());
    EXPECT_FALSE(renderer->Initialize()) << "Second initialization should fail";
    
    renderer->Shutdown();
}

TEST_F(RenderingEngineTest, InitializeWithSpecificAPI) {
    // Test with auto selection
    EXPECT_TRUE(renderer->Initialize(GraphicsAPI::Auto));
    EXPECT_TRUE(renderer->IsInitialized());
    
    auto device = renderer->GetDevice();
    ASSERT_NE(device, nullptr);
    
    // Verify device is initialized
    EXPECT_TRUE(device->IsInitialized());
    
    renderer->Shutdown();
}

// Frame management tests
TEST_F(RenderingEngineTest, FrameLifecycle) {
    ASSERT_TRUE(renderer->Initialize());
    
    EXPECT_NO_THROW(renderer->BeginFrame());
    EXPECT_NO_THROW(renderer->Render());
    EXPECT_NO_THROW(renderer->EndFrame());
    
    // Frame count should increment
    EXPECT_EQ(renderer->GetFrameCount(), 1u);
}

TEST_F(RenderingEngineTest, MultipleFrames) {
    ASSERT_TRUE(renderer->Initialize());
    
    const uint32_t numFrames = 10;
    for (uint32_t i = 0; i < numFrames; ++i) {
        renderer->BeginFrame();
        renderer->Render();
        renderer->EndFrame();
    }
    
    EXPECT_EQ(renderer->GetFrameCount(), numFrames);
}

TEST_F(RenderingEngineTest, FrameOperationsWithoutInitialization) {
    // Should not crash when not initialized
    EXPECT_NO_THROW(renderer->BeginFrame());
    EXPECT_NO_THROW(renderer->Render());
    EXPECT_NO_THROW(renderer->EndFrame());
    
    EXPECT_EQ(renderer->GetFrameCount(), 0u);
}

// Texture resource tests
TEST_F(RenderingEngineTest, CreateTexture) {
    ASSERT_TRUE(renderer->Initialize());
    
    TextureDesc desc{};
    desc.width = 256;
    desc.height = 256;
    desc.format = TextureFormat::RGBA8;
    
    auto handle = renderer->CreateTexture(desc);
    EXPECT_TRUE(handle.IsValid());
    
    renderer->DestroyTexture(handle);
}

TEST_F(RenderingEngineTest, CreateMultipleTextures) {
    ASSERT_TRUE(renderer->Initialize());
    
    std::vector<TextureHandle> textures;
    const int numTextures = 10;
    
    for (int i = 0; i < numTextures; ++i) {
        TextureDesc desc{};
        desc.width = 128;
        desc.height = 128;
        desc.format = TextureFormat::RGBA8;
        
        auto handle = renderer->CreateTexture(desc);
        EXPECT_TRUE(handle.IsValid());
        textures.push_back(handle);
    }
    
    // All handles should be unique
    for (size_t i = 0; i < textures.size(); ++i) {
        for (size_t j = i + 1; j < textures.size(); ++j) {
            EXPECT_FALSE(textures[i] == textures[j]) << "Texture handles should be unique";
        }
    }
    
    // Clean up
    for (auto handle : textures) {
        renderer->DestroyTexture(handle);
    }
}

TEST_F(RenderingEngineTest, UpdateTexture) {
    ASSERT_TRUE(renderer->Initialize());
    
    TextureDesc desc{};
    desc.width = 64;
    desc.height = 64;
    desc.format = TextureFormat::RGBA8;
    
    auto handle = renderer->CreateTexture(desc);
    ASSERT_TRUE(handle.IsValid());
    
    // Create some test data
    std::vector<uint8_t> data(64 * 64 * 4, 255);
    
    EXPECT_NO_THROW(renderer->UpdateTexture(handle, data.data(), data.size()));
    
    renderer->DestroyTexture(handle);
}

// Buffer resource tests
TEST_F(RenderingEngineTest, CreateBuffer) {
    ASSERT_TRUE(renderer->Initialize());
    
    BufferDesc desc{};
    desc.size = 1024;
    desc.type = BufferType::Vertex;
    
    auto handle = renderer->CreateBuffer(desc);
    EXPECT_TRUE(handle.IsValid());
    
    renderer->DestroyBuffer(handle);
}

TEST_F(RenderingEngineTest, CreateBufferWithInitialData) {
    ASSERT_TRUE(renderer->Initialize());
    
    std::vector<float> vertices = {
        0.0f, 0.5f, 0.0f,
        -0.5f, -0.5f, 0.0f,
        0.5f, -0.5f, 0.0f
    };
    
    BufferDesc desc{};
    desc.size = vertices.size() * sizeof(float);
    desc.type = BufferType::Vertex;
    desc.initialData = vertices.data();
    
    auto handle = renderer->CreateBuffer(desc);
    EXPECT_TRUE(handle.IsValid());
    
    renderer->DestroyBuffer(handle);
}

TEST_F(RenderingEngineTest, UpdateBuffer) {
    ASSERT_TRUE(renderer->Initialize());
    
    BufferDesc desc{};
    desc.size = 1024;
    desc.type = BufferType::Vertex;
    desc.dynamic = true;
    
    auto handle = renderer->CreateBuffer(desc);
    ASSERT_TRUE(handle.IsValid());
    
    std::vector<float> data(256, 1.0f);
    EXPECT_NO_THROW(renderer->UpdateBuffer(handle, data.data(), data.size() * sizeof(float)));
    
    renderer->DestroyBuffer(handle);
}

// Shader resource tests
TEST_F(RenderingEngineTest, CreateShader) {
    ASSERT_TRUE(renderer->Initialize());
    
    ShaderDesc desc{};
    desc.stage = ShaderStage::Vertex;
    desc.source = "void main() { gl_Position = vec4(0.0); }";
    
    auto handle = renderer->CreateShader(desc);
    EXPECT_TRUE(handle.IsValid());
    
    renderer->DestroyShader(handle);
}

TEST_F(RenderingEngineTest, CompileShader) {
    ASSERT_TRUE(renderer->Initialize());
    
    std::string vertexShader = R"(
        #version 450
        layout(location = 0) in vec3 position;
        void main() {
            gl_Position = vec4(position, 1.0);
        }
    )";
    
    auto handle = renderer->CompileShader(vertexShader, ShaderStage::Vertex);
    EXPECT_TRUE(handle.IsValid());
    
    renderer->DestroyShader(handle);
}

// Mesh resource tests
TEST_F(RenderingEngineTest, CreateMesh) {
    ASSERT_TRUE(renderer->Initialize());
    
    MeshData meshData{};
    meshData.vertices = {
        0.0f, 0.5f, 0.0f,
        -0.5f, -0.5f, 0.0f,
        0.5f, -0.5f, 0.0f
    };
    meshData.vertexCount = 3;
    
    auto handle = renderer->CreateMesh(meshData);
    EXPECT_TRUE(handle.IsValid());
    
    renderer->DestroyMesh(handle);
}

TEST_F(RenderingEngineTest, CreateIndexedMesh) {
    ASSERT_TRUE(renderer->Initialize());
    
    MeshData meshData{};
    meshData.vertices = {
        -0.5f, -0.5f, 0.0f,
        0.5f, -0.5f, 0.0f,
        0.5f, 0.5f, 0.0f,
        -0.5f, 0.5f, 0.0f
    };
    meshData.vertexCount = 4;
    
    meshData.indices = {0, 1, 2, 2, 3, 0};
    meshData.indexCount = 6;
    
    auto handle = renderer->CreateMesh(meshData);
    EXPECT_TRUE(handle.IsValid());
    
    renderer->DestroyMesh(handle);
}

TEST_F(RenderingEngineTest, UpdateMesh) {
    ASSERT_TRUE(renderer->Initialize());
    
    MeshData meshData{};
    meshData.vertices = {
        0.0f, 0.5f, 0.0f,
        -0.5f, -0.5f, 0.0f,
        0.5f, -0.5f, 0.0f
    };
    meshData.vertexCount = 3;
    
    auto handle = renderer->CreateMesh(meshData);
    ASSERT_TRUE(handle.IsValid());
    
    // Update mesh with new data
    meshData.vertices = {
        0.0f, 1.0f, 0.0f,
        -1.0f, -1.0f, 0.0f,
        1.0f, -1.0f, 0.0f
    };
    
    EXPECT_NO_THROW(renderer->UpdateMesh(handle, meshData));
    
    renderer->DestroyMesh(handle);
}

// Material resource tests
TEST_F(RenderingEngineTest, CreateMaterial) {
    ASSERT_TRUE(renderer->Initialize());
    
    auto handle = renderer->CreateMaterial();
    EXPECT_TRUE(handle.IsValid());
    
    renderer->DestroyMaterial(handle);
}

TEST_F(RenderingEngineTest, SetMaterialTexture) {
    ASSERT_TRUE(renderer->Initialize());
    
    auto material = renderer->CreateMaterial();
    ASSERT_TRUE(material.IsValid());
    
    TextureDesc texDesc{};
    texDesc.width = 256;
    texDesc.height = 256;
    texDesc.format = TextureFormat::RGBA8;
    
    auto texture = renderer->CreateTexture(texDesc);
    ASSERT_TRUE(texture.IsValid());
    
    EXPECT_NO_THROW(renderer->SetMaterialTexture(material, texture, 0));
    
    renderer->DestroyMaterial(material);
    renderer->DestroyTexture(texture);
}

TEST_F(RenderingEngineTest, SetMaterialShader) {
    ASSERT_TRUE(renderer->Initialize());
    
    auto material = renderer->CreateMaterial();
    ASSERT_TRUE(material.IsValid());
    
    ShaderDesc shaderDesc{};
    shaderDesc.stage = ShaderStage::Vertex;
    shaderDesc.source = "void main() {}";
    
    auto shader = renderer->CreateShader(shaderDesc);
    ASSERT_TRUE(shader.IsValid());
    
    EXPECT_NO_THROW(renderer->SetMaterialShader(material, shader));
    
    renderer->DestroyMaterial(material);
    renderer->DestroyShader(shader);
}

// Rendering pipeline tests
TEST_F(RenderingEngineTest, SubmitRenderObject) {
    ASSERT_TRUE(renderer->Initialize());
    
    MeshData meshData{};
    meshData.vertices = {0.0f, 0.5f, 0.0f, -0.5f, -0.5f, 0.0f, 0.5f, -0.5f, 0.0f};
    meshData.vertexCount = 3;
    
    auto mesh = renderer->CreateMesh(meshData);
    ASSERT_TRUE(mesh.IsValid());
    
    auto material = renderer->CreateMaterial();
    ASSERT_TRUE(material.IsValid());
    
    RenderObject obj{};
    obj.mesh = mesh;
    obj.material = material;
    obj.visible = true;
    
    // Initialize transform to identity matrix
    for (int i = 0; i < 16; ++i) {
        obj.transform[i] = (i % 5 == 0) ? 1.0f : 0.0f;
    }
    
    EXPECT_NO_THROW(renderer->SubmitRenderObject(obj));
    
    renderer->DestroyMesh(mesh);
    renderer->DestroyMaterial(material);
}

TEST_F(RenderingEngineTest, RenderWithObjects) {
    ASSERT_TRUE(renderer->Initialize());
    
    MeshData meshData{};
    meshData.vertices = {0.0f, 0.5f, 0.0f, -0.5f, -0.5f, 0.0f, 0.5f, -0.5f, 0.0f};
    meshData.vertexCount = 3;
    
    auto mesh = renderer->CreateMesh(meshData);
    ASSERT_TRUE(mesh.IsValid());
    
    auto material = renderer->CreateMaterial();
    ASSERT_TRUE(material.IsValid());
    
    RenderObject obj{};
    obj.mesh = mesh;
    obj.material = material;
    obj.visible = true;
    
    for (int i = 0; i < 16; ++i) {
        obj.transform[i] = (i % 5 == 0) ? 1.0f : 0.0f;
    }
    
    renderer->SubmitRenderObject(obj);
    
    renderer->BeginFrame();
    EXPECT_NO_THROW(renderer->Render());
    renderer->EndFrame();
    
    // Draw call count should be incremented
    EXPECT_GT(renderer->GetDrawCallCount(), 0u);
    
    renderer->DestroyMesh(mesh);
    renderer->DestroyMaterial(material);
}

TEST_F(RenderingEngineTest, ClearRenderQueue) {
    ASSERT_TRUE(renderer->Initialize());
    
    MeshData meshData{};
    meshData.vertices = {0.0f, 0.5f, 0.0f, -0.5f, -0.5f, 0.0f, 0.5f, -0.5f, 0.0f};
    meshData.vertexCount = 3;
    
    auto mesh = renderer->CreateMesh(meshData);
    ASSERT_TRUE(mesh.IsValid());
    
    auto material = renderer->CreateMaterial();
    ASSERT_TRUE(material.IsValid());
    
    RenderObject obj{};
    obj.mesh = mesh;
    obj.material = material;
    obj.visible = true;
    
    for (int i = 0; i < 16; ++i) {
        obj.transform[i] = (i % 5 == 0) ? 1.0f : 0.0f;
    }
    
    renderer->SubmitRenderObject(obj);
    renderer->ClearRenderQueue();
    
    // After clearing, rendering should not produce draw calls
    renderer->BeginFrame();
    renderer->Render();
    renderer->EndFrame();
    
    EXPECT_EQ(renderer->GetDrawCallCount(), 0u);
    
    renderer->DestroyMesh(mesh);
    renderer->DestroyMaterial(material);
}

TEST_F(RenderingEngineTest, RenderMultipleObjects) {
    ASSERT_TRUE(renderer->Initialize());
    
    const int numObjects = 5;
    std::vector<MeshHandle> meshes;
    std::vector<MaterialHandle> materials;
    
    for (int i = 0; i < numObjects; ++i) {
        MeshData meshData{};
        meshData.vertices = {0.0f, 0.5f, 0.0f, -0.5f, -0.5f, 0.0f, 0.5f, -0.5f, 0.0f};
        meshData.vertexCount = 3;
        
        auto mesh = renderer->CreateMesh(meshData);
        ASSERT_TRUE(mesh.IsValid());
        meshes.push_back(mesh);
        
        auto material = renderer->CreateMaterial();
        ASSERT_TRUE(material.IsValid());
        materials.push_back(material);
        
        RenderObject obj{};
        obj.mesh = mesh;
        obj.material = material;
        obj.visible = true;
        
        for (int j = 0; j < 16; ++j) {
            obj.transform[j] = (j % 5 == 0) ? 1.0f : 0.0f;
        }
        
        renderer->SubmitRenderObject(obj);
    }
    
    renderer->BeginFrame();
    renderer->Render();
    renderer->EndFrame();
    
    // Should have draw calls for all objects
    EXPECT_EQ(renderer->GetDrawCallCount(), static_cast<uint32_t>(numObjects));
    
    // Clean up
    for (auto mesh : meshes) {
        renderer->DestroyMesh(mesh);
    }
    for (auto material : materials) {
        renderer->DestroyMaterial(material);
    }
}

// Edge case tests
TEST_F(RenderingEngineTest, DestroyInvalidHandles) {
    ASSERT_TRUE(renderer->Initialize());
    
    TextureHandle invalidTexture{};
    BufferHandle invalidBuffer{};
    ShaderHandle invalidShader{};
    MeshHandle invalidMesh{};
    MaterialHandle invalidMaterial{};
    
    // Should not crash
    EXPECT_NO_THROW(renderer->DestroyTexture(invalidTexture));
    EXPECT_NO_THROW(renderer->DestroyBuffer(invalidBuffer));
    EXPECT_NO_THROW(renderer->DestroyShader(invalidShader));
    EXPECT_NO_THROW(renderer->DestroyMesh(invalidMesh));
    EXPECT_NO_THROW(renderer->DestroyMaterial(invalidMaterial));
}

TEST_F(RenderingEngineTest, CreateResourcesWithoutInitialization) {
    TextureDesc texDesc{};
    texDesc.width = 256;
    texDesc.height = 256;
    texDesc.format = TextureFormat::RGBA8;
    
    auto texture = renderer->CreateTexture(texDesc);
    EXPECT_FALSE(texture.IsValid()) << "Should not create texture without initialization";
    
    BufferDesc bufDesc{};
    bufDesc.size = 1024;
    bufDesc.type = BufferType::Vertex;
    
    auto buffer = renderer->CreateBuffer(bufDesc);
    EXPECT_FALSE(buffer.IsValid()) << "Should not create buffer without initialization";
    
    ShaderDesc shaderDesc{};
    shaderDesc.stage = ShaderStage::Vertex;
    shaderDesc.source = "void main() {}";
    
    auto shader = renderer->CreateShader(shaderDesc);
    EXPECT_FALSE(shader.IsValid()) << "Should not create shader without initialization";
}
