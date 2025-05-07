#include <cnoid/SimpleController>
//rosのライブラリ
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <memory>
#include <thread>
#include <mutex>

class MobileRobotDriveController : public cnoid::SimpleController{
public:
	virtual bool configure(cnoid::SimpleControllerConfig* config) override;
	virtual bool initialize(cnoid::SimpleControllerIO* io) override;
	virtual bool control() override;
	virtual void unconfigure() override;
	
private:
	cnoid::Link* wheels[2];
	cnoid::Link* arms[2];
	rclcpp::Node::SharedPtr node;
	rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription;
	rclcpp::Subscription<geometry_msgs::msg::Vector3>::SharedPtr subscriptionArm1;
	rclcpp::Subscription<geometry_msgs::msg::Vector3>::SharedPtr subscriptionArm2;
	geometry_msgs::msg::Twist command;
	geometry_msgs::msg::Vector3 commandArm1;
	geometry_msgs::msg::Vector3 commandArm2;
	rclcpp::executors::StaticSingleThreadedExecutor::UniquePtr executor;
	std::thread executorThread;
	std::mutex commandMutex;
	double diff[2] = {0.0, 0.0};
	double sumErrorArms[2] = {0.0, 0.0};
	double prevArms[2] = {0.0, 0.0};
};

//これはマクロの様子。
CNOID_IMPLEMENT_SIMPLE_CONTROLLER_FACTORY(MobileRobotDriveController)

bool MobileRobotDriveController::configure(cnoid::SimpleControllerConfig* config){
	printf("start config\n");
	node = std::make_shared<rclcpp::Node>(config->controllerName());
	
	subscription = node->create_subscription<geometry_msgs::msg::Twist>(
		"/cmd_vel", 1, [this](const geometry_msgs::msg::Twist::SharedPtr msg){
			std::lock_guard<std::mutex> lock(commandMutex);
			command = *msg;
			});
	subscriptionArm1 = node->create_subscription<geometry_msgs::msg::Vector3>(
		"/cmd_arm1_angle", 1, [this](const geometry_msgs::msg::Vector3::SharedPtr msg){
			std::lock_guard<std::mutex> lock(commandMutex);
			commandArm1 = *msg;
			});
	subscriptionArm2 = node->create_subscription<geometry_msgs::msg::Vector3>(
		"/cmd_arm2_angle", 1, [this](const geometry_msgs::msg::Vector3::SharedPtr msg){
			std::lock_guard<std::mutex> lock(commandMutex);
			commandArm2 = *msg;
			});
			
	executor = std::make_unique<rclcpp::executors::StaticSingleThreadedExecutor>();
	executor->add_node(node);
	executorThread = std::thread([this](){executor->spin();});

	printf("end config\n");

	return true;
}

bool MobileRobotDriveController::initialize(cnoid::SimpleControllerIO* io){
	printf("start init\n");
	auto body = io->body();
	wheels[0] = body->joint("LeftWheel");
	wheels[1] = body->joint("RightWheel");
	arms[0] = body->joint("Arm1Joint");
	arms[1] = body->joint("Arm2Joint");	

	for(int i = 0; i < 2; i++){
		auto wheel = wheels[i];
		wheel->setActuationMode(JointTorque);
		io->enableInput(wheel, JointVelocity);
		io->enableOutput(wheel, JointTorque);
		auto arm = arms[i];
		arm->setActuationMode(JointTorque);
		io->enableInput(arm, JointAngle);
		io->enableOutput(arm, JointTorque);
	}
	printf("end init\n");
	
	return true;
}

bool MobileRobotDriveController::control(){
	constexpr double wheelRadius = 0.076;
	constexpr double halfAxleWidth = 0.145;
	constexpr double kd = 0.5;
	constexpr double ki = 0.0001;
	constexpr double kpArm = 100.0;
	constexpr double kiArm = 0.00;
	constexpr double kdArm = 0.0;
	
	double dq_target[2];
	double angleTarget[2];
	
	//executor->spin_some();
	//printf("start control\n");
	
	{
		std::lock_guard<std::mutex> lock(commandMutex);
		double dq_x = command.linear.x / wheelRadius;
		double dq_yaw = command.angular.z * halfAxleWidth /wheelRadius;
		dq_target[0] = dq_x - dq_yaw;
		dq_target[1] = dq_x + dq_yaw;
		
		if(dq_target[0] == 0 && dq_target[1] == 0){
			diff[0] = 0.0;
			diff[1] = 0.0;
		}
		angleTarget[0] = commandArm1.y;
		angleTarget[1] = commandArm2.y;
		
	}
	
	for(int i = 0; i < 2; i++){
		auto wheel = wheels[i];
		double diffTmp = dq_target[i] - wheel->dq();
		wheel->u() = kd * diffTmp + ki * diff[i];
		diff[i] += diffTmp;
		
		auto arm = arms[i];
		double errorPosArm = angleTarget[i] - arm->q();
		double speedPosArm = prevArms[i] - arm->q();
		arm->u() = kpArm * errorPosArm + kiArm * sumErrorArms[i] + kdArm * speedPosArm;
		sumErrorArms[i] += errorPosArm;
		printf("%d, %f, %f, %f, %f\n", i, angleTarget[i], errorPosArm, sumErrorArms[i], speedPosArm);
	}

	//printf("end control\n");
	
	return true;
}


void MobileRobotDriveController::unconfigure(){
	if(executor){
		executor->cancel();
		executorThread.join();
		executor->remove_node(node);
		executor.reset();
	}
}

