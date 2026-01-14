#pragma once

#include <cmath>
#include <algorithm>

namespace pywrkgame {
namespace physics {

// Simple 3D vector
struct Vec3 {
    float x, y, z;
    
    Vec3() : x(0.0f), y(0.0f), z(0.0f) {}
    Vec3(float x, float y, float z) : x(x), y(y), z(z) {}
    
    Vec3 operator+(const Vec3& other) const {
        return Vec3(x + other.x, y + other.y, z + other.z);
    }
    
    Vec3 operator-(const Vec3& other) const {
        return Vec3(x - other.x, y - other.y, z - other.z);
    }
    
    Vec3 operator*(float scalar) const {
        return Vec3(x * scalar, y * scalar, z * scalar);
    }
    
    Vec3 operator/(float scalar) const {
        return Vec3(x / scalar, y / scalar, z / scalar);
    }
    
    Vec3& operator+=(const Vec3& other) {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }
    
    float dot(const Vec3& other) const {
        return x * other.x + y * other.y + z * other.z;
    }
    
    float length() const {
        return std::sqrt(x * x + y * y + z * z);
    }
    
    Vec3 normalized() const {
        float len = length();
        if (len > 0.0f) {
            return *this / len;
        }
        return Vec3(0.0f, 0.0f, 0.0f);
    }
    
    float distance(const Vec3& other) const {
        return (*this - other).length();
    }
};

// Simple 2D vector
struct Vec2 {
    float x, y;
    
    Vec2() : x(0.0f), y(0.0f) {}
    Vec2(float x, float y) : x(x), y(y) {}
    
    Vec2 operator+(const Vec2& other) const {
        return Vec2(x + other.x, y + other.y);
    }
    
    Vec2 operator-(const Vec2& other) const {
        return Vec2(x - other.x, y - other.y);
    }
    
    Vec2 operator*(float scalar) const {
        return Vec2(x * scalar, y * scalar);
    }
    
    Vec2 operator/(float scalar) const {
        return Vec2(x / scalar, y / scalar);
    }
    
    Vec2& operator+=(const Vec2& other) {
        x += other.x;
        y += other.y;
        return *this;
    }
    
    float dot(const Vec2& other) const {
        return x * other.x + y * other.y;
    }
    
    float length() const {
        return std::sqrt(x * x + y * y);
    }
    
    Vec2 normalized() const {
        float len = length();
        if (len > 0.0f) {
            return *this / len;
        }
        return Vec2(0.0f, 0.0f);
    }
};

// Simple quaternion
struct Quat {
    float w, x, y, z;
    
    Quat() : w(1.0f), x(0.0f), y(0.0f), z(0.0f) {}
    Quat(float w, float x, float y, float z) : w(w), x(x), y(y), z(z) {}
    
    static Quat identity() {
        return Quat(1.0f, 0.0f, 0.0f, 0.0f);
    }
};

} // namespace physics
} // namespace pywrkgame
