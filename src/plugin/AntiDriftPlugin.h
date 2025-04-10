#ifndef ANTI_DRIFT_PLUGIN_H
#define ANTI_DRIFT_PLUGIN_H

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

class AntiDriftPlugin {
public:
    AntiDriftPlugin();
    void initialize(float driftThreshold, float filterCoefficient);
    void update(const SensorData& sensorData);
    Pose getCorrectedPose();
    void calibratePosition(const char* position);
    bool isDriftDetected();
    void resetCalibration();

private:
    float driftThreshold;
    float filterCoefficient;
    Pose correctedPose;
    Pose referencePose;
    bool isCalibrated;
    std::string currentPosition;
    std::vector<Pose> calibrationHistory;

    void applyKalmanFilter(const SensorData& sensorData);
    void correctMovement();
    void updateGravityReference(const SensorData& sensorData);
    bool validateMovement(const Pose& newPose);
    void logDriftStatus();
};

#endif // ANTI_DRIFT_PLUGIN_H
