#include "AntiDriftAlgorithm.h"
#include <cmath>
#include <iostream>

AntiDriftAlgorithm::AntiDriftAlgorithm() : driftThreshold(0.0f), filterCoefficient(0.0f), isCalibrated(false) {
    // Initialize poses to zero
    for(int i = 0; i < 3; i++) {
        correctedPose.position[i] = 0.0f;
        correctedPose.rotation[i] = 0.0f;
        referencePose.position[i] = 0.0f;
        referencePose.rotation[i] = 0.0f;
    }
}

void AntiDriftAlgorithm::initialize(float driftThreshold, float filterCoefficient) {
    this->driftThreshold = driftThreshold;
    this->filterCoefficient = filterCoefficient;
    isCalibrated = false;
    std::cout << "Initialized AntiDriftAlgorithm with threshold: " << driftThreshold << std::endl;
}

void AntiDriftAlgorithm::update(const SensorData& sensorData) {
    if (!isCalibrated) {
        std::cerr << "Warning: System not calibrated. Please calibrate first." << std::endl;
        return;
    }

    // Update gravity reference first
    updateGravityReference(sensorData);
    
    // Apply Kalman filter to sensor data
    applyKalmanFilter(sensorData);
    
    // Validate and correct movement
    if (!validateMovement(correctedPose)) {
        correctMovement();
    }
    
    // Log status for debugging
    logDriftStatus();
}

void AntiDriftAlgorithm::applyKalmanFilter(const SensorData& sensorData) {
    // Implementation of Kalman filter for sensor fusion
    // This combines accelerometer, gyroscope, and magnetometer data
    
    float alpha = filterCoefficient;
    
    // Fuse accelerometer and gyroscope data
    for(int i = 0; i < 3; i++) {
        correctedPose.rotation[i] = alpha * (correctedPose.rotation[i] + sensorData.gyroscope[i]) + 
                                  (1.0f - alpha) * std::atan2(sensorData.accelerometer[i], 
                                   std::sqrt(sensorData.accelerometer[(i+1)%3] * sensorData.accelerometer[(i+1)%3] + 
                                           sensorData.accelerometer[(i+2)%3] * sensorData.accelerometer[(i+2)%3]));
    }
}

void AntiDriftAlgorithm::updateGravityReference(const SensorData& sensorData) {
    // Update gravity vector reference based on current position
    if (currentPosition == "lying") {
        // Adjust reference frame for lying position
        // The gravity vector should be perpendicular to the body
    } else {
        // Standard standing position reference
    }
}

bool AntiDriftAlgorithm::validateMovement(const Pose& newPose) {
    // Check if movement is physically possible
    // Returns false if movement exceeds natural limits
    
    const float MAX_ROTATION = 180.0f; // degrees
    const float MAX_POSITION_CHANGE = 1.0f; // meters
    
    for(int i = 0; i < 3; i++) {
        if (std::abs(newPose.rotation[i] - referencePose.rotation[i]) > MAX_ROTATION ||
            std::abs(newPose.position[i] - referencePose.position[i]) > MAX_POSITION_CHANGE) {
            return false;
        }
    }
    return true;
}

void AntiDriftAlgorithm::correctMovement() {
    // Apply constraints to correct invalid movements
    // This prevents unnatural poses and reduces drift
    
    const float CORRECTION_FACTOR = 0.8f;
    
    for(int i = 0; i < 3; i++) {
        // Gradually move back towards reference pose
        correctedPose.rotation[i] = correctedPose.rotation[i] * CORRECTION_FACTOR + 
                                  referencePose.rotation[i] * (1.0f - CORRECTION_FACTOR);
    }
}

void AntiDriftAlgorithm::calibratePosition(const char* position) {
    currentPosition = position;
    
    // Store current pose as reference
    referencePose = correctedPose;
    
    // Add to calibration history
    calibrationHistory.push_back(referencePose);
    
    isCalibrated = true;
    std::cout << "Calibrated for position: " << position << std::endl;
}

bool AntiDriftAlgorithm::isDriftDetected() {
    float totalDrift = 0.0f;
    
    // Calculate total drift from reference pose
    for(int i = 0; i < 3; i++) {
        totalDrift += std::abs(correctedPose.rotation[i] - referencePose.rotation[i]);
    }
    
    return totalDrift > driftThreshold;
}

void AntiDriftAlgorithm::logDriftStatus() {
    if (isDriftDetected()) {
        std::cout << "Warning: Significant drift detected!" << std::endl;
    }
}
