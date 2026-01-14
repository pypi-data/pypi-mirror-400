#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>

#include <opencv2/core/cuda.hpp>
#include <opencv2/cudaoptflow.hpp>
#include <opencv2/cudaarithm.hpp>
#include <opencv2/cudafeatures2d.hpp>
#include <opencv2/cudaimgproc.hpp>
#include <opencv2/cudawarping.hpp>


#include <opencv2/optflow/sparse_matching_gpc.hpp>


#include "hires_timer.hpp"


cv::cuda::GpuMat create_meshgrid_gpu( int width, int height )
{
	cv::Mat g(height, width, CV_32FC2);
	for (int i = 0; i < height; ++i) {
		for (int j = 0; j < width; ++j) {
			g.at< cv::Point2f >(i, j) = cv::Point2f( static_cast<float>(j), static_cast<float>(i) );
		}
	}

	return cv::cuda::GpuMat(g);
}


int main( int argc, char* argv[] )
{
	const std::string DIR("D:/dev/wassfast_testdata/wassfast_frames_dbg/");
	cvlab::HiresTimer timer;

	
#if 1

	std::cout << "Loading images" << std::endl;
	cv::Mat cam0P = cv::imread(DIR + std::string("cam0P.jpg"), cv::IMREAD_GRAYSCALE	);
	cv::Mat cam1P = cv::imread(DIR + std::string("cam1P.jpg"), cv::IMREAD_GRAYSCALE);

	
	cv::Ptr< cv::cuda::CornersDetector> corneralg = cv::cuda::createGoodFeaturesToTrackDetector(CV_8UC1, 10000, 0.0001, 10.0, 5, true /* useharris */, 0.01 /* harris k */ );

	cv::Ptr< cv::cuda::FarnebackOpticalFlow > flowalg = cv::cuda::FarnebackOpticalFlow::create(3, 0.5, true, 15, 10, 5, 1.5, 0);
	
	cv::cuda::GpuMat grid = create_meshgrid_gpu( cam0P.cols, cam0P.rows);

	std::cout << "Computing flow..." << std::endl;
	


	timer.start();

	for (int i = 0; i < 20; ++i)
	{
		cv::Mat aux;
		cam0P.convertTo(aux, CV_8UC1);
		cv::cuda::GpuMat cam0Pc(cam0P);
		cam1P.convertTo(aux, CV_8UC1);
		cv::cuda::GpuMat cam1Pc(cam1P);


		cv::cuda::GpuMat corners;
		corneralg->detect(cam0Pc, corners, cv::noArray() );

		cv::cuda::GpuMat flowc01;
		flowalg->calc(cam0Pc, cam1Pc, flowc01 );

#if 1
		cv::cuda::GpuMat flowc10;
		flowalg->calc(cam1Pc, cam0Pc, flowc10 );

		cv::cuda::GpuMat remapxy;
		cv::cuda::add(grid, flowc01, remapxy);

		std::vector< cv::cuda::GpuMat > remap_channels;
		cv::cuda::split(remapxy, remap_channels );

		std::vector< cv::cuda::GpuMat > flowc10_warped_channels(2);
		std::vector< cv::cuda::GpuMat > flowc10_channels;
		cv::cuda::split(flowc10, flowc10_channels );

		cv::cuda::remap(flowc10_channels[0], flowc10_warped_channels[0], remap_channels[0], remap_channels[1], cv::INTER_LINEAR);
		cv::cuda::remap(flowc10_channels[1], flowc10_warped_channels[1], remap_channels[0], remap_channels[1], cv::INTER_LINEAR);

		cv::cuda::GpuMat flowc10_warped;
		cv::cuda::merge(flowc10_warped_channels, flowc10_warped);
	
		cv::cuda::GpuMat flowerror_uv;
		cv::cuda::subtract(flowc10, flowc10_warped, flowerror_uv);

		cv::cuda::GpuMat flowerror_mag;
		cv::cuda::magnitudeSqr(flowerror_uv, flowerror_mag);
#endif

#if 0
		corners.download(aux);
		cv::Mat dbg;
		cv::cvtColor(cam0P, dbg, cv::COLOR_GRAY2BGR);

		std::cout <<  aux.cols << " features found." << std::endl;
		for (int i = 0; i < aux.cols; ++i) 
		{
			cv::drawMarker(dbg, aux.at<cv::Point2f>(i), cv::Scalar(255, 0, 0));
		}
		cv::imshow("keypoints", dbg);
		cv::waitKey(0);
		
		/*
		std::vector< cv::KeyPoint > keypoints;
		featalg->convert(gpukeypoints, keypoints);
		std::cout << keypoints.size() << " keypoints extracted" << std::endl;

		cv::Mat keypimg;
		cv::drawKeypoints(cam0P, keypoints, keypimg);
		cv::imshow("keypoints", keypimg);
		cv::waitKey(0);
		*/


		cv::Mat mask;
		flowerror_mag.download(mask);
		
		cv::cuda::GpuMat cam1Pc_warped;
		cv::cuda::remap(cam1Pc, cam1Pc_warped, remap_channels[0], remap_channels[1], cv::INTER_LINEAR);
		cv::Mat cam1P_warped;
		cam1Pc_warped.download(cam1P_warped);

		cam1P_warped.convertTo(aux, CV_8UC1);
		cv::imwrite("00.png", cam0P);
		cv::imwrite("11.png", cam1P);
		cv::imwrite("01.png", aux );
		cv::imwrite("mask.png", (mask<0.5));
		cv::imwrite("keypoints.png", dbg);
#endif	
		
	}

	std::cout << "Done in " << timer.elapsed()/20.0 << " seconds." << std::endl;

#endif

	/*
	std::vector< std::pair< cv::Point2i, cv::Point2i > > matches;
	cv::Ptr< cv::optflow::GPCForest< 1 > > gpc = cv::optflow::GPCForest< 1 >::create();
	std::cout << "Computing flow... " << std::endl;
	gpc->findCorrespondences(cam0P, cam1P, matches);
	std::cout << "Done! " << std::endl;

	std::cout << "N matches found: " << matches.size();
	*/

	/*
	std::cout << "Creating NvidiaOpticalFlow_1_0 instance" << std::endl;
	cv::Ptr< cv::cuda::NvidiaHWOpticalFlow > cudaflow = cv::cuda::NvidiaOpticalFlow_1_0::create( cam0P.cols, cam0P.rows );
	std::cout << "CUDA HWOpticalFlow grid size: " << cudaflow->getGridSize() << std::endl;
	*/

	/*
	cv::Ptr< cv::cuda::DenseOpticalFlow > cudaflow = cv::cuda::BroxOpticalFlow::create();

	
	cv::cuda::GpuMat flowc;

	cv::Mat aux;
	cam0P.convertTo(aux, CV_32FC1);
	cv::cuda::GpuMat cam0Pc( aux );

	cam1P.convertTo(aux, CV_32FC1);
	cv::cuda::GpuMat cam1Pc(aux);

	std::cout << "Computing flow..." << std::endl;
	cudaflow->calc(cam0Pc, cam1Pc, flowc);
	std::cout << "Done!" << std::endl;
	
	*/

#if 0

	cv::Mat flow;
	flowc01.download(flow);

	
	std::cout << "Flow type: " << flow.type() << std::endl;

	std::vector< cv::Mat > flow_channels;
	cv::split(flow, flow_channels);
	std::cout << "Flow channels: " << flow_channels.size() << std::endl;

	cv::imshow("test", (flow_channels[0]+10)/4096.0*255.0 );
	cv::waitKey(0);
#endif

	return 0;
}
