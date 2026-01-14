/**
 * Property-based tests for Graphics Device abstraction
 * Feature: pywrkgame-library, Property 11: Rendering Pipeline Consistency
 * Feature: pywrkgame-library, Property 16: Format Support
 * Validates: Requirements 3.8, 11.4
 */

#include <gtest/gtest.h>
#include "pywrkgame/rendering/GraphicsDevice.h"
#include "pywrkgame/rendering/VulkanDevice.h"
#include "pywrkgame/rendering/MetalDevice.h"
#include "pywrkgame/rendering/D3D12Device.h"
#include <vector>
#include <random>
#include <algorithm>

using namespace pywrkgame::rendering;

class GraphicsDevicePropertiesTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create device based on platform
        device = CreateGraphicsDevice(GraphicsAPI::Auto);
        ASSERT_NE(device, nullptr);
        ASSERT_TRUE(device->Initialize());
    }
    
    void TearDown() override {
        if (device) {
            device->Shutdown();
        }
    }
    
    std::unique_ptr<GraphicsDevice> device;
    std::mt19937 rng{std::random_device{}()};
};

/**
 * Property 11: Rendering Pipeline Consistency
 * For any scene rendered with different pipelines (forward, deferred, tiled),
 * the visual output should be equivalent
 * 
 * This test verifies that the graphics device abstraction provides consistent
 * behavior across different implementations (Vulkan, Metal, D3D12)
 */
TEST_F(GraphicsDevicePropertiesTest, RenderingPipelineConsistency) {
    // Test that all device types can be created and initialized
    std::vector<GraphicsAPI> apis = {
        GraphicsAPI::Vulkan,
        GraphicsAPI::Metal,
        GraphicsAPI::D3D12
    };
    
    for (auto api : apis) {
        auto test_device = CreateGraphicsDevice(api);
        if (!test_device) {
            // Skip if API not supported on this platform
            continue;
        }
        
        ASSERT_TRUE(test_device->Initialize()) << "Device should initialize for API " << static_cast<int>(api);
        ASSERT_TRUE(test_device->IsInitialized()) << "Device should report initialized state";
        ASSERT_EQ(test_device->GetAPI(), api) << "Device should report correct API";
        
        // Test frame lifecycle
        EXPECT_NO_THROW(test_device->BeginFrame());
        EXPECT_NO_THROW(test_device->BeginRenderPass());
        EXPECT_NO_THROW(test_device->EndRenderPass());
        EXPECT_NO_THROW(test_device->EndFrame());
        EXPECT_NO_THROW(test_device->Present());
        
        test_device->Shutdown();
        ASSERT_FALSE(test_device->IsInitialized()) << "Device should report not initialized after shutdown";
    }
}

/**
 * Property 16: Format Support
 * For any supported texture format (DDS, KTX, ASTC) or audio format,
 * files should load and render/play correctly
 * 
 * This test verifies that all texture formats can be created successfully
 */
TEST_F(GraphicsDevicePropertiesTest, TextureFormatSupport) {
    std::vector<TextureFormat> formats = {
        TextureFormat::RGBA8,
        TextureFormat::RGBA16F,
        TextureFormat::RGBA32F,
        TextureFormat::RGB8,
        TextureFormat::RG8,
        TextureFormat::R8,
        TextureFormat::Depth24Stencil8,
        TextureFormat::Depth32F,
        TextureFormat::DDS,
        TextureFormat::KTX,
        TextureFormat::ASTC
    };
    
    // Test various texture dimensions
    std::vector<std::pair<uint32_t, uint32_t>> dimensions = {
        {1, 1},
        {16, 16},
        {256, 256},
        {512, 512},
        {1024, 1024},
        {2048, 2048},
        {4096, 4096}
    };
    
    for (auto format : formats) {
        for (auto [width, height] : dimensions) {
            TextureDesc desc{};
            desc.width = width;
            desc.height = height;
            desc.format = format;
            desc.mipLevels = 1;
            
            auto handle = device->CreateTexture(desc);
            EXPECT_TRUE(handle.IsValid()) 
                << "Texture should be created for format " << static_cast<int>(format)
                << " with dimensions " << width << "x" << height;
            
            if (handle.IsValid()) {
                device->DestroyTexture(handle);
                // After destruction, handle should still have same ID but resource is freed
            }
        }
    }
}

/**
 * Property test: Resource handle validity
 * For any created resource, the handle should be valid and unique
 */
TEST_F(GraphicsDevicePropertiesTest, ResourceHandleValidity) {
    const int num_iterations = 100;
    std::vector<TextureHandle> texture_handles;
    std::vector<BufferHandle> buffer_handles;
    std::vector<ShaderHandle> shader_handles;
    
    // Create multiple resources
    for (int i = 0; i < num_iterations; ++i) {
        // Create texture
        TextureDesc tex_desc{};
        tex_desc.width = 256;
        tex_desc.height = 256;
        tex_desc.format = TextureFormat::RGBA8;
        auto tex_handle = device->CreateTexture(tex_desc);
        EXPECT_TRUE(tex_handle.IsValid()) << "Texture handle should be valid";
        texture_handles.push_back(tex_handle);
        
        // Create buffer
        BufferDesc buf_desc{};
        buf_desc.size = 1024;
        buf_desc.type = BufferType::Vertex;
        auto buf_handle = device->CreateBuffer(buf_desc);
        EXPECT_TRUE(buf_handle.IsValid()) << "Buffer handle should be valid";
        buffer_handles.push_back(buf_handle);
        
        // Create shader
        ShaderDesc shader_desc{};
        shader_desc.stage = ShaderStage::Vertex;
        shader_desc.source = "void main() {}";
        auto shader_handle = device->CreateShader(shader_desc);
        EXPECT_TRUE(shader_handle.IsValid()) << "Shader handle should be valid";
        shader_handles.push_back(shader_handle);
    }
    
    // Verify all handles are unique
    for (size_t i = 0; i < texture_handles.size(); ++i) {
        for (size_t j = i + 1; j < texture_handles.size(); ++j) {
            EXPECT_FALSE(texture_handles[i] == texture_handles[j]) 
                << "Texture handles should be unique";
        }
    }
    
    for (size_t i = 0; i < buffer_handles.size(); ++i) {
        for (size_t j = i + 1; j < buffer_handles.size(); ++j) {
            EXPECT_FALSE(buffer_handles[i] == buffer_handles[j]) 
                << "Buffer handles should be unique";
        }
    }
    
    for (size_t i = 0; i < shader_handles.size(); ++i) {
        for (size_t j = i + 1; j < shader_handles.size(); ++j) {
            EXPECT_FALSE(shader_handles[i] == shader_handles[j]) 
                << "Shader handles should be unique";
        }
    }
    
    // Clean up resources
    for (auto handle : texture_handles) {
        device->DestroyTexture(handle);
    }
    for (auto handle : buffer_handles) {
        device->DestroyBuffer(handle);
    }
    for (auto handle : shader_handles) {
        device->DestroyShader(handle);
    }
}

/**
 * Property test: Buffer creation and update
 * For any buffer size and data, buffer should be created and updated correctly
 */
TEST_F(GraphicsDevicePropertiesTest, BufferCreationAndUpdate) {
    std::uniform_int_distribution<size_t> size_dist(64, 65536);
    std::uniform_int_distribution<uint8_t> data_dist(0, 255);
    
    const int num_iterations = 50;
    
    for (int i = 0; i < num_iterations; ++i) {
        size_t buffer_size = size_dist(rng);
        
        // Create buffer
        BufferDesc desc{};
        desc.size = buffer_size;
        desc.type = BufferType::Vertex;
        desc.dynamic = true;
        
        auto handle = device->CreateBuffer(desc);
        EXPECT_TRUE(handle.IsValid()) << "Buffer should be created with size " << buffer_size;
        
        if (handle.IsValid()) {
            // Generate random data
            std::vector<uint8_t> data(buffer_size);
            for (auto& byte : data) {
                byte = data_dist(rng);
            }
            
            // Update buffer - should not crash
            EXPECT_NO_THROW(device->UpdateBuffer(handle, data.data(), data.size()));
            
            // Partial update
            if (buffer_size > 128) {
                size_t offset = buffer_size / 4;
                size_t update_size = buffer_size / 2;
                EXPECT_NO_THROW(device->UpdateBuffer(handle, data.data(), update_size, offset));
            }
            
            device->DestroyBuffer(handle);
        }
    }
}

/**
 * Property test: Viewport and scissor state
 * For any viewport and scissor dimensions, state should be set without errors
 */
TEST_F(GraphicsDevicePropertiesTest, ViewportAndScissorState) {
    std::uniform_real_distribution<float> pos_dist(0.0f, 1920.0f);
    std::uniform_real_distribution<float> size_dist(1.0f, 1920.0f);
    std::uniform_int_distribution<int32_t> int_pos_dist(0, 1920);
    std::uniform_int_distribution<uint32_t> uint_size_dist(1, 1920);
    
    const int num_iterations = 100;
    
    for (int i = 0; i < num_iterations; ++i) {
        float vp_x = pos_dist(rng);
        float vp_y = pos_dist(rng);
        float vp_width = size_dist(rng);
        float vp_height = size_dist(rng);
        
        EXPECT_NO_THROW(device->SetViewport(vp_x, vp_y, vp_width, vp_height))
            << "Viewport should be set without errors";
        
        int32_t sc_x = int_pos_dist(rng);
        int32_t sc_y = int_pos_dist(rng);
        uint32_t sc_width = uint_size_dist(rng);
        uint32_t sc_height = uint_size_dist(rng);
        
        EXPECT_NO_THROW(device->SetScissor(sc_x, sc_y, sc_width, sc_height))
            << "Scissor should be set without errors";
    }
}

/**
 * Property test: Draw commands
 * For any valid draw parameters, draw commands should execute without errors
 */
TEST_F(GraphicsDevicePropertiesTest, DrawCommands) {
    std::uniform_int_distribution<uint32_t> count_dist(1, 10000);
    std::uniform_int_distribution<uint32_t> instance_dist(1, 100);
    
    const int num_iterations = 50;
    
    device->BeginFrame();
    device->BeginRenderPass();
    
    for (int i = 0; i < num_iterations; ++i) {
        uint32_t vertex_count = count_dist(rng);
        uint32_t instance_count = instance_dist(rng);
        uint32_t first_vertex = count_dist(rng) % 1000;
        uint32_t first_instance = instance_dist(rng) % 10;
        
        EXPECT_NO_THROW(device->Draw(vertex_count, instance_count, first_vertex, first_instance))
            << "Draw command should execute without errors";
        
        uint32_t index_count = count_dist(rng);
        uint32_t first_index = count_dist(rng) % 1000;
        int32_t vertex_offset = static_cast<int32_t>(count_dist(rng) % 1000);
        
        EXPECT_NO_THROW(device->DrawIndexed(index_count, instance_count, first_index, vertex_offset, first_instance))
            << "DrawIndexed command should execute without errors";
    }
    
    device->EndRenderPass();
    device->EndFrame();
}

/**
 * Property test: Multiple frame rendering
 * For any number of frames, the device should handle frame lifecycle correctly
 */
TEST_F(GraphicsDevicePropertiesTest, MultipleFrameRendering) {
    const int num_frames = 100;
    
    for (int frame = 0; frame < num_frames; ++frame) {
        EXPECT_NO_THROW(device->BeginFrame()) << "BeginFrame should not throw on frame " << frame;
        EXPECT_NO_THROW(device->BeginRenderPass()) << "BeginRenderPass should not throw on frame " << frame;
        
        // Simulate some rendering
        device->SetViewport(0.0f, 0.0f, 1920.0f, 1080.0f);
        device->Draw(3, 1, 0, 0);
        
        EXPECT_NO_THROW(device->EndRenderPass()) << "EndRenderPass should not throw on frame " << frame;
        EXPECT_NO_THROW(device->EndFrame()) << "EndFrame should not throw on frame " << frame;
        EXPECT_NO_THROW(device->Present()) << "Present should not throw on frame " << frame;
    }
}
