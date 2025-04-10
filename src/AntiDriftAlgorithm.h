#ifndef ANTI_DRIFT_ALGORITHM_H
#define ANTI_DRIFT_ALGORITHM_H

#include <vector>
#include <string>

struct SensorData {
    float accelerometer[3];
    float gyroscope[3];
    float magnetometer[3];
};

struct Pose {
    float position[3];
    float rotation[3];
};

class AntiDriftAlgorithm {
public:
    AntiDriftAlgorithm();
    void initialize(float driftThreshold, float filterCoefficient);
    void update(const SensorData& sensorData);
    Pose getCorrectedPose();
    void calibratePosition(const char* position); // "standing" or "lying"
    bool isDriftDetected();
    void resetCalibration();

private:
    // Kalman filter parameters
    float driftThreshold;
    float filterCoefficient;
    Pose correctedPose;
    Pose referencePose;
    
    // Calibration states
    bool isCalibrated;
    std::string currentPosition;
    std::vector<Pose> calibrationHistory;

    // Private methods
    void applyKalmanFilter(const SensorData& sensorData);
    void correctMovement();
    void updateGravityReference(const SensorData& sensorData);
    bool validateMovement(const Pose& newPose);
    void logDriftStatus();
};

#endif // ANTI_DRIFT_ALGORITHM_H
