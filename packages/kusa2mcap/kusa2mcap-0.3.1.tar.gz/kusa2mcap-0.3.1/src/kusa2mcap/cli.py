#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2024 KUSA ADS Team. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# 将kusa ads protobuf数据转换为foxglove protobuf数据并写入mcap文件
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import sys
import click
import math
from collections import defaultdict
from io import BytesIO
import struct
from typing import IO, Any, Dict, Optional, Tuple, Union
from typing import Dict, Type
from google.protobuf.message import Message
# kusa ads protobuf
from kusa_ads_protobuf.openads.proto.common.underlay_message_pb2 import MessageStream
from kusa_ads_protobuf.openads.proto.canbus.chassis_pb2 import Chassis
from kusa_ads_protobuf.openads.proto.canbus.chassis_detail_pb2 import ChassisDetail
from kusa_ads_protobuf.openads.proto.planning.planning_pb2 import ADCTrajectory
from kusa_ads_protobuf.openads.proto.planning.planning_status_pb2 import PlanningStatus
from kusa_ads_protobuf.openads.proto.control.control_cmd_pb2 import ControlCommand
from kusa_ads_protobuf.openads.proto.control.pad_msg_pb2 import PadMessage
from kusa_ads_protobuf.openads.proto.localization.localization_pb2 import LocalizationEstimate
from kusa_ads_protobuf.openads.proto.perception.perception_obstacle_pb2 import PerceptionObstacles
from kusa_ads_protobuf.openads.proto.drivers.pointcloud_pb2 import PointCloud as KusaPointCloud
from kusa_ads_protobuf.openads.proto.drivers.gnss.imu_pb2 import Imu
from kusa_ads_protobuf.openads.proto.perception.traffic_light_detection_pb2 import TrafficLightDetection
from kusa_ads_protobuf.openads.proto.perception.traffic_light_detection_pb2 import TrafficLight
from kusa_ads_protobuf.openads.proto.drivers.sensor_image_pb2 import CompressedImage as KusaCompressedImage
from kusa_ads_protobuf.openads.proto.monitor.system_status_pb2 import DiagnosticArray as KusaDiagnosticArray
from kusa_ads_protobuf.openads.proto.monitor.system_status_pb2 import FaultMessage
from kusa_ads_protobuf.openads.proto.monitor.system_status_pb2 import EmergenceMessage
from kusa_ads_protobuf.openads.proto.monitor.system_status_pb2 import SystemDiagnostic as KusaSystemDiagnostic
from kusa_ads_protobuf.openads.proto.monitor.system_status_pb2 import HmiLog
from kusa_ads_protobuf.openads.proto.dataservice.data_service_grpc_api_pb2 import TaskConfig
from kusa_ads_protobuf.openads.proto.dataservice.data_service_grpc_api_pb2 import CameraListInfo
from kusa_ads_protobuf.openads.proto.dataservice.data_service_grpc_api_pb2 import FileInfoList
from kusa_ads_protobuf.openads.proto.vtx.vtx_cloud_pb2 import Vtx_vehicleStatus
from kusa_ads_protobuf.openads.proto.vtx.vtx_cloud_pb2 import Vtx_vehicleEvent
from kusa_ads_protobuf.openads.proto.vtx.vtx_cloud_pb2 import Vtx_taskInfo
from kusa_ads_protobuf.openads.proto.prediction.prediction_obstacle_pb2 import PredictionObstacles
from kusa_ads_protobuf.openads.proto.perception.perception_anything_pb2 import PerceptionAnythings
# foxglove protobuf
from foxglove_schemas_protobuf.PackedElementField_pb2 import PackedElementField
from foxglove_schemas_protobuf.PointCloud_pb2 import PointCloud as FoxglovePointCloud
from foxglove_schemas_protobuf.Pose_pb2 import Pose as FoxglovePose
from foxglove_schemas_protobuf.PoseInFrame_pb2 import PoseInFrame as FoxglovePoseInFrame
from foxglove_schemas_protobuf.Quaternion_pb2 import Quaternion
from foxglove_schemas_protobuf.Vector3_pb2 import Vector3
from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
from foxglove_schemas_protobuf.CircleAnnotation_pb2 import CircleAnnotation
from foxglove_schemas_protobuf.Color_pb2 import Color
from foxglove_schemas_protobuf.ImageAnnotations_pb2 import ImageAnnotations
from foxglove_schemas_protobuf.Point2_pb2 import Point2
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage as FoxgloveCompressedImage
from foxglove_schemas_protobuf.Log_pb2 import Log as FoxgloveLog
from foxglove_schemas_protobuf.LocationFix_pb2 import LocationFix as FoxgloveLocationFix
from foxglove_schemas_protobuf.FrameTransforms_pb2 import FrameTransforms as FoxgloveFrameTransforms
from foxglove_schemas_protobuf.SceneEntity_pb2 import SceneEntity
from foxglove_schemas_protobuf.SceneUpdate_pb2 import SceneUpdate


from google.protobuf.timestamp_pb2 import Timestamp
# mcap protobuf writer
from mcap_protobuf.writer import Writer

SUPPORTED_TYPES = ["image", "pointcloud"]

def validate_only(ctx, param, value):
    if value and value not in SUPPORTED_TYPES:
        raise click.BadParameter(f"Only supports: {', '.join(SUPPORTED_TYPES)}")
    return value

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Parse Kusa record files to MCAP format."""
    if ctx.invoked_subcommand is None:
        click.echo(f"Usage: {sys.argv[0]} [OPTIONS] COMMAND [ARGS]...")
        click.echo("Try '--help' for help.")
        ctx.exit(1)

@cli.command()
@click.argument('input_dir', required=True, type=click.Path(exists=True))
@click.option('-o', '--output', required=True, type=click.Path(), help='Output MCAP file path')
@click.option('--no-image', is_flag=True, help='Skip converting images')
@click.option('--no-pointcloud', is_flag=True, help='Skip converting point clouds')
# @click.option('--only', type=click.Choice(SUPPORTED_TYPES), callback=validate_only,
#               help='Convert ONLY this type (overrides --no-* flags)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def convert(input_dir, output, no_image, no_pointcloud, verbose):
    """
    Convert record files to MCAP.
    
    You can disable specific types with --no-* to convert just one type.
    """
    global option_no_image
    global option_no_pointcloud
    global option_verbose
    option_no_image = no_image
    option_no_pointcloud = no_pointcloud
    option_verbose = verbose
    # click.echo(f"Converting types: {sorted(convert_types)}")
    click.echo(f"Input dir: {input_dir}")
    click.echo(f"Output: {output}")
    start_time = Timestamp()
    start_time.GetCurrentTime()
    # print(f"Start time: {start_time.seconds} seconds.")
    # 遍历目录，查找所以rec_x的文件，并排序，没有后缀，实例名如rec_0, rec_1, rec_2 ... rec_10, rec_11等
    rec_files = []
    for filename in os.listdir(input_dir):
        if filename.startswith("rec_"):
            rec_files.append(os.path.join(input_dir, filename))
    rec_files.sort(key=lambda x: int(x.split("_")[-1]))
    # 获取地图偏移量
    global map_offset
    if len(rec_files) == 0:
        map_offset = (0.0, 0.0)
    else:
        map_offset = get_map_offset_from_record(rec_files[0])
    click.secho(f"Map offset: x={map_offset[0]}, y={map_offset[1]}", fg="yellow")
    # 打印找到的record文件数量
    click.secho(f"Found {len(rec_files)} record files to convert.", fg="green")
    # 实例化mcap writer
    with open(output, "wb") as f, Writer(f) as mcap_writer:
        # 逐个解析record文件
        for rec_file in rec_files:
            click.echo(f"Parsing record file: {rec_file}")
            parse_record_file(rec_file, mcap_writer)
        # 打印topic消息数量统计
        click.echo("Topic message count:")
        for topic, count in topic_message_count.items():
            click.echo(f"  {topic}: {count}")

    # convert_types = set(SUPPORTED_TYPES)
    # if no_image:
    #     convert_types.discard("image")
    # if no_pointcloud:
    #     convert_types.discard("pointcloud")

    # if verbose:
    


    
    end_time = Timestamp()
    end_time.GetCurrentTime()
    # print(f"End time: {end_time.seconds} seconds.")
    click.secho(f"✅ Converted {input_dir} file(s) to {output}. Time taken: {end_time.seconds - start_time.seconds} seconds.", fg="green")

@cli.command()
@click.argument('input_dir', required=True, type=click.Path(exists=True))
# --show-info-file 参数指定通过record目录下的info文件显示统计信息
@click.option('--show-info-file', is_flag=True, help='Show info from record info file')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed stats')
def stats(input_dir, show_info_file, verbose):
    """Show statistics of record files (message counts per topic)."""
    # 统计目录下名称为 rec_ 开头的文件数量
    rec_files_count = 0
    for filename in os.listdir(input_dir):
        if filename.startswith("rec_"):
            rec_files_count += 1

    # 如果 --show-info-file 参数被指定
    if show_info_file:
        # 查找 input_dir 下的 info 文件，并打印内容
        info_file = os.path.join(input_dir, "info")
        if os.path.isfile(info_file):
            click.echo(f"Info file in {input_dir}:")
            with open(info_file, "r") as f:
                info_content = f.read()
                click.echo(info_content)
        else:
            click.echo(f"No info file found in {input_dir}.")
        return
    else:
        # 通过 count_messages_in_record_dir 函数统计消息数量
        total_topic_message_count = count_messages_in_record_dir(input_dir)
    # 统计数据

    click.echo(f"Total record files: {rec_files_count}")
    for topic, count in total_topic_message_count.items():
        click.echo(f"  {topic} : {count}")

# 函数 第record文件中查找第一个定位topic，解析并拿到x,y作为地图偏移量
def get_map_offset_from_record(input_record_file: str) -> Tuple[float, float]:
    with open(input_record_file, 'rb') as f:
        file_stream = f.read()       
        messageStream = MessageStream()
        messageStream.ParseFromString(file_stream)
        # 查找第一个定位topic
        for ul_msg in messageStream.messages:
            if ul_msg.topic_name == "rt/openads/slam/esekf_odom_gnss_fused_pose":
                # 解析定位消息
                localization = LocalizationEstimate()
                localization.ParseFromString(ul_msg.data)
                x = localization.pose.position.x
                y = localization.pose.position.y
                return x, y
    # 如果没有找到定位topic，返回0,0
    return 0.0, 0.0

# 函数 遍历input record目录下的所有rec_x文件，按顺序统计所有topic的消息数量
def count_messages_in_record_dir(input_record_dir: str) -> Dict[str, int]:
    # 打印检查中，请等待
    click.echo("Counting messages, please wait...")
    from collections import defaultdict
    topic_message_count = defaultdict(int)
    total_messages = 0
    # 遍历目录，查找所以rec_x的文件，并排序，没有后缀，实例名如rec_0, rec_1, rec_2 ... rec_10, rec_11等
    rec_files = []
    for filename in os.listdir(input_record_dir):
        if filename.startswith("rec_"):
            rec_files.append(os.path.join(input_record_dir, filename))
    rec_files.sort(key=lambda x: int(x.split("_")[-1]))
    # 逐个解析record文件
    for rec_file in rec_files:
        with open(rec_file, 'rb') as f:
            file_stream = f.read()       
            messageStream = MessageStream()
            messageStream.ParseFromString(file_stream)
            # 统计每个topic的消息数量
            for ul_msg in messageStream.messages:
                if ul_msg.topic_name not in topic_message_count:
                    topic_message_count[ul_msg.topic_name] = 0
                topic_message_count[ul_msg.topic_name] += 1
                total_messages += 1
    topic_message_count["__total_messages__"] = total_messages
    return topic_message_count

# 函数，构建datatype名称和kusa ads protobuf message class的映射
def build_message_class_map(*message_classes):
    return {
        cls.DESCRIPTOR.full_name: cls
        for cls in message_classes
    }

# 函数，解析kusa ads record 文件
# 参数1：record file路径
def parse_record_file(record_file, mcap_writer: Writer):
    # global map_offset
    # click.secho(f"Map offset: x={map_offset[0]}, y={map_offset[1]}", fg="yellow")
    global option_no_image
    global option_no_pointcloud
    global option_verbose
    if option_no_image and option_verbose:
        click.secho("Note: Image conversion is disabled.", fg="yellow")
    if option_no_pointcloud and option_verbose:
        click.secho("Note: PointCloud conversion is disabled.", fg="yellow")
    # 声明使用全局变量
    global topic_message_count
    global kusa_compressed_image_datatype
    global kusa_pointcloud_datatype
    with open(record_file, 'rb') as f:
        file_stream = f.read()       
        messageStream = MessageStream()
        messageStream.ParseFromString(file_stream)
        
        # 打印所有message的datatype
        for ul_msg in messageStream.messages:
            if ul_msg.data_type == kusa_compressed_image_datatype:
                if not option_no_image:
                    kusa_compressed_image = KusaCompressedImage()
                    kusa_compressed_image.ParseFromString(ul_msg.data)
                    convert_KusaCompressedImage_to_FoxgloveCompressedImage(kusa_compressed_image, mcap_writer, ul_msg.topic_name, ul_msg.timestamp)
            elif ul_msg.data_type == kusa_pointcloud_datatype:
                if not option_no_pointcloud:
                    kusa_pointcloud = KusaPointCloud()
                    kusa_pointcloud.ParseFromString(ul_msg.data)
                    convert_KusaPointCloud_to_FoxglovePointCloud(kusa_pointcloud, mcap_writer, ul_msg.topic_name, ul_msg.timestamp)
            elif ul_msg.data_type == kusa_localization_datatype:
                if ul_msg.topic_name == "rt/openads/slam/esekf_odom_gnss_fused_pose":
                    kusa_localization = LocalizationEstimate()
                    kusa_localization.ParseFromString(ul_msg.data)
                    convert_KusaLocalization_to_FoxglovePose(kusa_localization, mcap_writer, ul_msg.topic_name, ul_msg.timestamp)
                # 无论如何都写入原始消息
                write_raw_underlay_message_to_mcap(ul_msg, mcap_writer, ul_msg.timestamp)
            elif ul_msg.data_type == kusa_hmi_log_datatype:
                if ul_msg.topic_name == "rt/openads/monitor/hmi_log":
                    hmi_log = HmiLog()
                    hmi_log.ParseFromString(ul_msg.data)
                    convert_HmiLog_to_FoxgloveLog(hmi_log, mcap_writer, ul_msg.topic_name, ul_msg.timestamp)
                # 无论如何都写入原始消息
                write_raw_underlay_message_to_mcap(ul_msg, mcap_writer, ul_msg.timestamp)
            elif ul_msg.data_type == kusa_adctrajectory_datatype:
                if ul_msg.topic_name == "rt/openads/planning/planning":
                    kusa_adctrajectory = ADCTrajectory()
                    kusa_adctrajectory.ParseFromString(ul_msg.data)
                    convert_KusaADCTrajectory_to_FoxgloveSceneUpdate(kusa_adctrajectory, mcap_writer, ul_msg.topic_name, ul_msg.timestamp)
                # 无论如何都写入原始消息
                write_raw_underlay_message_to_mcap(ul_msg, mcap_writer, ul_msg.timestamp)
            elif ul_msg.data_type == kusa_PredictionObstacles_datatype:
                if ul_msg.topic_name == "rt/openads/prediction/obstacles":
                    kusa_predictionobstacles = PredictionObstacles()
                    kusa_predictionobstacles.ParseFromString(ul_msg.data)
                    convert_KusaPredictionObstacles_to_FoxgloveSceneUpdate(kusa_predictionobstacles, mcap_writer, ul_msg.topic_name, ul_msg.timestamp)
                # 无论如何都写入原始消息
                write_raw_underlay_message_to_mcap(ul_msg, mcap_writer, ul_msg.timestamp)
            else:
                # print(f"Unknown datatype: {ul_msg.data_type}, writing raw data.")
                write_raw_underlay_message_to_mcap(ul_msg, mcap_writer, ul_msg.timestamp)

# 函数 转换 kusa planning ADCTrajectory 为 foxglove SceneUpdate，并写入mcap文件
def convert_KusaADCTrajectory_to_FoxgloveSceneUpdate(kusa_adctrajectory, mcap_writer, channel_name, ts: Optional[Timestamp] = None):
    # 设置时间戳
    timestamp = Timestamp()
    timestamp.seconds = int(ts)
    timestamp.nanos = int((ts - timestamp.seconds) * 1e9)
    channel_name = "/hmi/map/planning"
    foxglove_scene_update = parse_PlanningTrajectory_to_SceneUpdate(kusa_adctrajectory,timestamp)
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_scene_update,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )
    channel_name = "/hmi/map/planning_polygons"
    foxglove_scene_update_polygons = parse_PlanningPolygons_to_SceneUpdate(kusa_adctrajectory,timestamp)
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_scene_update_polygons,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )
    channel_name = "/hmi/map/planning_boundary"
    foxglove_scene_update_boundaries = parse_PlanningBoundaries_to_SceneUpdate(kusa_adctrajectory,timestamp)
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_scene_update_boundaries,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

# 函数 将 单个 kusa pre obs 转换为 foxglove SceneUpdate entity
def convert_single_KusaPredictionObstacle_to_SceneEntity(obstacle, timestamp: Optional[Timestamp] = None, is_special_obstacle=False) -> SceneEntity:
    entity = SceneEntity()
    entity.frame_id = "world"
    entity.frame_locked = True
    if is_special_obstacle:
        entity.id = f"special_obstacle_{obstacle.perception_obstacle.id}"
    else:
        entity.id = f"obstacle_{obstacle.perception_obstacle.id}"
    if timestamp is not None:
        entity.timestamp.CopyFrom(timestamp)
    # 根据障碍物类型，设置不同的颜色
    # double r, g, b, a;
    r = 0.545098039
    g = 0.545098039
    b = 0.478431373
    a = 0.8
    # 判断障碍物类型
    if obstacle.perception_obstacle.type == obstacle.perception_obstacle.UNKNOWN:
        r = 0.545098039
        g = 0.545098039
        b = 0.478431373
        a = 0.8
    elif obstacle.perception_obstacle.type == obstacle.perception_obstacle.UNKNOWN_MOVABLE:
        r = 1.0
        g = 0.6
        b = 0.0
        a = 0.8
    elif obstacle.perception_obstacle.type == obstacle.perception_obstacle.UNKNOWN_UNMOVABLE:
        r = 1.0
        g = 0.0
        b = 1.0
        a = 0.8
    elif obstacle.perception_obstacle.type == obstacle.perception_obstacle.PEDESTRIAN:
        r = 1.0
        g = 0.2
        b = 0.0
        a = 0.8
    elif obstacle.perception_obstacle.type == obstacle.perception_obstacle.BICYCLE:
        r = 0.2
        g = 0.0
        b = 1.0
        a = 0.8
    elif obstacle.perception_obstacle.type == obstacle.perception_obstacle.VEHICLE:
        r = 0.0
        g = 1.0
        b = 0.0
        a = 0.8
    else:
        r = 0.545098039
        g = 0.545098039
        b = 0.478431373
        a = 0.8
    # 创建一个text 表示 obs id
    text_entity = entity.texts.add()
    if is_special_obstacle:
        text_entity.text = f"S_{str(obstacle.perception_obstacle.id)}"
    else:
        text_entity.text = str(obstacle.perception_obstacle.id)
    text_entity.billboard = True
    text_entity.font_size = 0.2
    text_entity.color.r = r
    text_entity.color.g = g
    text_entity.color.b = b
    text_entity.color.a = a
    text_entity.pose.position.x = obstacle.perception_obstacle.position.x - map_offset[0]
    text_entity.pose.position.y = obstacle.perception_obstacle.position.y - map_offset[1]
    text_entity.pose.position.z = 0.0
    # 用线画出障碍物的边界
    obs_line = entity.lines.add()
    obs_line.thickness = 2
    obs_line.scale_invariant = True
    obs_line.type = obs_line.LINE_LOOP
    obs_line.color.r = r
    obs_line.color.g = g
    obs_line.color.b = b
    obs_line.color.a = a
    obs_line.pose.orientation.w = 1.0
    obs_line.pose.orientation.x = 0.0
    obs_line.pose.orientation.y = 0.0
    obs_line.pose.orientation.z = 0.0
    for point in obstacle.perception_obstacle.polygon_point:
        p = obs_line.points.add()
        p.x = point.x - map_offset[0]
        p.y = point.y - map_offset[1]
        p.z = 0.05
    # 用箭头画出障碍物的朝向
    arrow_entity = entity.arrows.add()
    arrow_entity.shaft_length = 0.5
    arrow_entity.shaft_diameter = 0.05
    arrow_entity.head_length = 0.25
    arrow_entity.head_diameter = 0.1
    arrow_entity.color.r = r
    arrow_entity.color.g = g
    arrow_entity.color.b = b
    arrow_entity.color.a = a
    arrow_entity.pose.position.x = obstacle.perception_obstacle.position.x - map_offset[0]
    arrow_entity.pose.position.y = obstacle.perception_obstacle.position.y - map_offset[1]
    arrow_entity.pose.position.z = 0.0
    # 箭头指向障碍物的朝向
    # obstacle.perception_obstacle.theta 转换为四元数
    arrow_entity.pose.orientation.w = math.cos(obstacle.perception_obstacle.theta / 2.0)
    arrow_entity.pose.orientation.x = 0.0
    arrow_entity.pose.orientation.y = 0.0
    arrow_entity.pose.orientation.z = math.sin(obstacle.perception_obstacle.theta / 2.0)
    # obs traj 
    vel = obstacle.perception_obstacle.velocity
    abs_vel = math.sqrt(vel.x * vel.x + vel.y * vel.y)
    if abs_vel > 0.3 and len(obstacle.trajectory) > 0:
        obs_traj = entity.lines.add()
        obs_traj.thickness = 2
        obs_traj.scale_invariant = True
        obs_traj.type = obs_traj.LINE_LIST
        obs_traj.color.r = r
        obs_traj.color.g = g
        obs_traj.color.b = b
        obs_traj.color.a = a
        obs_traj.pose.orientation.w = 1.0
        obs_traj.pose.orientation.x = 0.0
        obs_traj.pose.orientation.y = 0.0
        obs_traj.pose.orientation.z = 0.0
        size = len(obstacle.trajectory[0].trajectory_point)
        point0 = obstacle.trajectory[0].trajectory_point[0]
        p0 = obs_traj.points.add()
        p0.x = point0.path_point.x - map_offset[0]
        p0.y = point0.path_point.y - map_offset[1]
        p0.z = 0.05
        point1 = obstacle.trajectory[0].trajectory_point[size - 1]
        p1 = obs_traj.points.add()
        p1.x = point1.path_point.x - map_offset[0]
        p1.y = point1.path_point.y - map_offset[1]
        p1.z = 0.05
    return entity

# 函数 转换 PredictionObstacles 为 foxglove SceneUpdate，并写入mcap文件
def convert_KusaPredictionObstacles_to_FoxgloveSceneUpdate(kusa_predictionobstacles, mcap_writer, channel_name, ts: Optional[Timestamp] = None):
    # 设置时间戳
    timestamp = Timestamp()
    timestamp.seconds = int(ts)
    timestamp.nanos = int((ts - timestamp.seconds) * 1e9)
    channel_name = "/hmi/map/prediction_obstacles"
    foxglove_scene_update = SceneUpdate()
    # 遍历所有障碍物
    for obstacle in kusa_predictionobstacles.prediction_obstacle:
        entity = convert_single_KusaPredictionObstacle_to_SceneEntity(obstacle, timestamp, is_special_obstacle=False)
        foxglove_scene_update.entities.append(entity)
    for special_obstacle in kusa_predictionobstacles.prediction_special_obstacle:
        entity = convert_single_KusaPredictionObstacle_to_SceneEntity(special_obstacle, timestamp, is_special_obstacle=True)
        foxglove_scene_update.entities.append(entity)
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_scene_update,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

# 函数 解析 kusa planning ADCTrajectory 中的规划点 返回 foxglove SceneUpdate
def parse_PlanningTrajectory_to_SceneUpdate(kusa_adctrajectory, timestamp: Optional[Timestamp] = None) -> SceneUpdate:
    foxglove_scene_update = SceneUpdate()
    entity = foxglove_scene_update.entities.add()
    entity.frame_id = "world"
    entity.frame_locked = True
    entity.id = "planning_path"
    if timestamp is not None:
        entity.timestamp.CopyFrom(timestamp)
    routing_line = entity.lines.add()
    routing_line.thickness = 1.3
    routing_line.scale_invariant = False
    routing_line.type = routing_line.LINE_STRIP
    routing_line.color.r = 0.0
    routing_line.color.g = 0.749019608
    routing_line.color.b = 1.0
    routing_line.color.a = 0.049215686
    routing_line.pose.orientation.w = 1.0
    routing_line.pose.orientation.x = 0.0
    routing_line.pose.orientation.y = 0.0
    routing_line.pose.orientation.z = 0.0
    for point in kusa_adctrajectory.trajectory_point:
        p = routing_line.points.add()
        p.x = point.path_point.x - map_offset[0]
        p.y = point.path_point.y - map_offset[1]
        p.z = 0.0
    return foxglove_scene_update

# 函数 解析 kusa planning polygons 为 foxglove SceneUpdate
def parse_PlanningPolygons_to_SceneUpdate(kusa_adctrajectory, timestamp: Optional[Timestamp] = None) -> SceneUpdate:
    foxglove_scene_update = SceneUpdate()
    entity = foxglove_scene_update.entities.add()
    entity.frame_id = "world"
    entity.frame_locked = True
    entity.id = "planning_polygon"
    for polygon in kusa_adctrajectory.trajectory_point:
        line = entity.lines.add()
        line.thickness = 1.0
        line.scale_invariant = True
        line.type = line.LINE_LOOP
        line.color.r = 0.8
        line.color.g = 0.0
        line.color.b = 1.0
        line.color.a = 0.05
        line.pose.orientation.w = 1.0
        line.pose.orientation.x = 0.0
        line.pose.orientation.y = 0.0
        line.pose.orientation.z = 0.0
        for p_point in polygon.polygon_point:
            p = line.points.add()
            p.x = p_point.x - map_offset[0]
            p.y = p_point.y - map_offset[1]
            p.z = 0.0
    return foxglove_scene_update

# ParsePlanningBoundary
# 函数 解析 kusa planning boundaries 为 foxglove SceneUpdate
def parse_PlanningBoundaries_to_SceneUpdate(kusa_adctrajectory, timestamp: Optional[Timestamp] = None) -> SceneUpdate:
    foxglove_scene_update = SceneUpdate()
    entity = foxglove_scene_update.entities.add()
    entity.frame_id = "world"
    entity.frame_locked = True
    entity.id = "planning_boundary"
    # center line
    reference_center_line = entity.lines.add()
    reference_center_line.thickness = 1
    reference_center_line.scale_invariant = True
    reference_center_line.type = reference_center_line.LINE_STRIP
    reference_center_line.color.r = 0.0
    reference_center_line.color.g = 0.8
    reference_center_line.color.b = 1.0
    reference_center_line.color.a = 1
    reference_center_line.pose.orientation.w = 1.0
    reference_center_line.pose.orientation.x = 0.0
    reference_center_line.pose.orientation.y = 0.0
    reference_center_line.pose.orientation.z = 0.0
    for point in kusa_adctrajectory.reference_center_points:
        p = reference_center_line.points.add()
        p.x = point.x - map_offset[0]
        p.y = point.y - map_offset[1]
        p.z = 0.0

    # left_boundary
    left_boundary_line = entity.lines.add()
    left_boundary_line.thickness = 1
    left_boundary_line.scale_invariant = True
    left_boundary_line.type = left_boundary_line.LINE_STRIP
    left_boundary_line.color.r = 1.0
    left_boundary_line.color.g = 0.8
    left_boundary_line.color.b = 0.0
    left_boundary_line.color.a = 1
    left_boundary_line.pose.orientation.w = 1.0
    left_boundary_line.pose.orientation.x = 0.0
    left_boundary_line.pose.orientation.y = 0.0
    left_boundary_line.pose.orientation.z = 0.0
    for point in kusa_adctrajectory.reference_left_boundary_points:
        p = left_boundary_line.points.add()
        p.x = point.x - map_offset[0]
        p.y = point.y - map_offset[1]
        p.z = 0.0

    #  right_boundary
    right_boundary_line = entity.lines.add()
    right_boundary_line.thickness = 1
    right_boundary_line.scale_invariant = True
    right_boundary_line.type = right_boundary_line.LINE_STRIP
    right_boundary_line.color.r = 1.0
    right_boundary_line.color.g = 0.8
    right_boundary_line.color.b = 0.0
    right_boundary_line.color.a = 1
    right_boundary_line.pose.orientation.w = 1.0
    right_boundary_line.pose.orientation.x = 0.0
    right_boundary_line.pose.orientation.y = 0.0
    right_boundary_line.pose.orientation.z = 0.0
    for point in kusa_adctrajectory.reference_right_boundary_points:
        p = right_boundary_line.points.add()
        p.x = point.x - map_offset[0]
        p.y = point.y - map_offset[1]
        p.z = 0.0
    return foxglove_scene_update


# 函数 转换hmi log为foxglove log，并写入mcap文件
def convert_HmiLog_to_FoxgloveLog(hmi_log, mcap_writer, channel_name, ts: Optional[Timestamp] = None):
    global topic_message_count
    # 统计topic消息数量
    if channel_name not in topic_message_count:
        topic_message_count[channel_name] = 0
    topic_message_count[channel_name] += 1
    # 设置时间戳
    timestamp = Timestamp()
    timestamp.seconds = int(ts)
    timestamp.nanos = int((ts - timestamp.seconds) * 1e9)
    channel_name = "/hmi/log"
    foxglove_log = FoxgloveLog()
    foxglove_log.level = hmi_log.level
    foxglove_log.message = hmi_log.message
    foxglove_log.file = hmi_log.file
    foxglove_log.line = hmi_log.line
    foxglove_log.name = hmi_log.name
    foxglove_log.timestamp.CopyFrom(timestamp)
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_log,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

# 函数 转换kusa ads CompressedImage为foxglove CompressedImage，并写入mcap文件
def convert_KusaCompressedImage_to_FoxgloveCompressedImage(kusa_compressed_image, mcap_writer, channel_name, ts: Optional[Timestamp] = None):
    global topic_message_count
    # 统计topic消息数量
    if channel_name not in topic_message_count:
        topic_message_count[channel_name] = 0
    topic_message_count[channel_name] += 1
    foxglove_compressed_image = FoxgloveCompressedImage()
    # 通过frame_id 获取对应的foxglove frame_id
    if kusa_compressed_image.header.frame_id in camera_frameid_map:
        foxglove_compressed_image.frame_id = camera_frameid_map[kusa_compressed_image.header.frame_id]
    else:
        foxglove_compressed_image.frame_id = kusa_compressed_image.header.frame_id
    foxglove_compressed_image.format = "jpeg"  # 假设kusa的压缩格式是jpeg
    foxglove_compressed_image.data = kusa_compressed_image.data
    # 设置时间戳
    timestamp = Timestamp()
    timestamp.seconds = int(ts)
    timestamp.nanos = int((ts - timestamp.seconds) * 1e9)
    foxglove_compressed_image.timestamp.CopyFrom(timestamp)
    # 获取对应的foxglove topic name
    if channel_name in camera_topic_map:
        channel_name = camera_topic_map[channel_name]
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_compressed_image,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

# 函数 转换kusa ads PointCloud为foxglove PointCloud，并写入mcap文件
def convert_KusaPointCloud_to_FoxglovePointCloud(kusa_pointcloud, mcap_writer, channel_name, ts: Optional[Timestamp] = None):
    # 打印kusa_pointcloud frame_id 和 点数量
    # print(f"Converting KusaPointCloud frame_id: {kusa_pointcloud.header.frame_id}, point count: {len(kusa_pointcloud.point)}")
    global topic_message_count
    # 统计topic消息数量
    if channel_name not in topic_message_count:
        topic_message_count[channel_name] = 0
    topic_message_count[channel_name] += 1
    # 转换为foxglove PointCloud
    fields = [
        PackedElementField(name="x", offset=0, type=PackedElementField.FLOAT32),
        PackedElementField(name="y", offset=4, type=PackedElementField.FLOAT32),
        PackedElementField(name="z", offset=8, type=PackedElementField.FLOAT32),
        PackedElementField(name="intensity", offset=12, type=PackedElementField.FLOAT32),
    ]
    pose = FoxglovePose(
        position=Vector3(x=0, y=0, z=0),
        orientation=Quaternion(w=1, x=0, y=0, z=0),
    )
    foxglove_pointcloud = FoxglovePointCloud()
    foxglove_pointcloud.frame_id = kusa_pointcloud.header.frame_id
    foxglove_pointcloud.point_stride = 16  # 每个点占用16字节
    foxglove_pointcloud.fields.extend(fields)
    foxglove_pointcloud.pose.CopyFrom(pose)
    data = BytesIO()
    for point in kusa_pointcloud.point:
        data.write(
            struct.pack(
                "<ffff",
                point.x,
                point.y,
                point.z,
                point.intensity,
            )
        )
    foxglove_pointcloud.data = data.getvalue()
    # 设置时间戳
    timestamp = Timestamp()
    timestamp.seconds = int(ts)
    timestamp.nanos = int((ts - timestamp.seconds) * 1e9)
    foxglove_pointcloud.timestamp.CopyFrom(timestamp)
    # 获取对应的foxglove topic name
    if channel_name in pointcloud_topic_map:
        channel_name = pointcloud_topic_map[channel_name]
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_pointcloud,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

# 函数 转换kusa ads LocalizationEstimate为foxglove Pose，并写入mcap文件
def convert_KusaLocalization_to_FoxglovePose(kusa_localization, mcap_writer, channel_name, ts: Optional[Timestamp] = None):
    global topic_message_count
    channel_name = "/hmi/tfs"

    timestamp = Timestamp()
    timestamp.seconds = int(ts)
    timestamp.nanos = int((ts - timestamp.seconds) * 1e9)

    FoxgloveTfs_msg = FoxgloveFrameTransforms()
    # 添加一个transform
    tf1 = FoxgloveTfs_msg.transforms.add()
    tf1.child_frame_id = "rtk"
    tf1.parent_frame_id = "world"
    tf1.timestamp.CopyFrom(timestamp)
    tf1.translation.x = kusa_localization.pose.position.x - map_offset[0]
    tf1.translation.y = kusa_localization.pose.position.y - map_offset[1]
    tf1.translation.z = kusa_localization.pose.position.z
    tf1.rotation.x = kusa_localization.pose.orientation.qx
    tf1.rotation.y = kusa_localization.pose.orientation.qy
    tf1.rotation.z = kusa_localization.pose.orientation.qz
    tf1.rotation.w = kusa_localization.pose.orientation.qw

    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=FoxgloveTfs_msg,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )
    channel_name = "/hmi/pose"

    foxglove_poseInFrame = FoxglovePoseInFrame()
    foxglove_poseInFrame.frame_id = "rtk"
    foxglove_poseInFrame.pose.orientation.x = 0
    foxglove_poseInFrame.pose.orientation.y = 0
    foxglove_poseInFrame.pose.orientation.z = 0
    foxglove_poseInFrame.pose.orientation.w = 1
    foxglove_poseInFrame.timestamp.CopyFrom(timestamp)
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_poseInFrame,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

    channel_name = "/hmi/gps"
    foxglove_location_fix = FoxgloveLocationFix()
    foxglove_location_fix.latitude = kusa_localization.longitude_latitude_height.lat
    foxglove_location_fix.longitude = kusa_localization.longitude_latitude_height.lon
    foxglove_location_fix.altitude = kusa_localization.longitude_latitude_height.height
    foxglove_location_fix.frame_id = "map"
    foxglove_location_fix.timestamp.CopyFrom(timestamp)
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=foxglove_location_fix,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

# 函数 mcap写入原始kusa ads protobuf消息
def write_raw_kusa_message_to_mcap(kusa_message: Any, mcap_writer: Writer, channel_name, ts: Optional[Timestamp] = None):
    # 根据 ul_message 的 data type 将消息解析为对应的protobuf消息
    global topic_message_count
    # 统计topic消息数量
    if channel_name not in topic_message_count:
        topic_message_count[channel_name] = 0
    topic_message_count[channel_name] += 1

    # 设置时间戳
    timestamp = Timestamp()
    timestamp.seconds = int(ts)
    timestamp.nanos = int((ts - timestamp.seconds) * 1e9)
    # 写入mcap文件
    mcap_writer.write_message(
        topic=channel_name,
        message=kusa_message,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

# 函数 mcap写入原始underlay message
def write_raw_underlay_message_to_mcap(ul_message: Any, mcap_writer: Writer, ts: Optional[Timestamp] = None):
    # 根据 ul_message 的 data type 将消息解析为对应的protobuf消息
    global topic_message_count
    global datatype_messageclass_map
    datatype = ul_message.data_type
    # print(f"Writing raw underlay message of datatype: {datatype}")
    kusa_message: Union[Any, bytes]
    if datatype in datatype_messageclass_map:
        MessageClass = datatype_messageclass_map[datatype]  # 得到类
        kusa_message = MessageClass()                                # 创建新实例
        kusa_message.ParseFromString(ul_message.data)                    # 反序列化
        # print("message_class:", MessageClass)
        # print("type(message_class):", type(MessageClass))
        # print("is callable?", callable(MessageClass))
        # 统计topic消息数量
        if ul_message.topic_name not in topic_message_count:
            topic_message_count[ul_message.topic_name] = 0
        topic_message_count[ul_message.topic_name] += 1
    else:
        print(f"Unknown datatype: {datatype}, return")
        return
    # print(f"Writing message of type: {type(kusa_message)}")
    # 设置时间戳
    timestamp = Timestamp()
    timestamp.seconds = int(ts)
    timestamp.nanos = int((ts - timestamp.seconds) * 1e9)

    # 写入mcap文件
    mcap_writer.write_message(
        topic=ul_message.topic_name,
        message=kusa_message,
        log_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
        publish_time=timestamp.seconds * 1_000_000_000 + timestamp.nanos,
    )

def main():
    # ======= 预制变量 =======
    # 新建一个datatype名称和kusa ads protobuf message class的映射
    global datatype_messageclass_map
    datatype_messageclass_map = build_message_class_map(
        LocalizationEstimate,
        PerceptionObstacles,
        Imu,
        TrafficLightDetection,
        TrafficLight,
        Chassis,
        ChassisDetail,
        ADCTrajectory,
        PlanningStatus,
        ControlCommand,
        KusaDiagnosticArray,
        FaultMessage,
        EmergenceMessage,
        KusaSystemDiagnostic,
        TaskConfig,
        CameraListInfo,
        Vtx_vehicleStatus,
        Vtx_vehicleEvent,
        Vtx_taskInfo,
        FileInfoList,
        PredictionObstacles,
        HmiLog,
        PerceptionAnythings,
        PadMessage,
    )
    # 定义目标datatype
    global kusa_compressed_image_datatype
    kusa_compressed_image_datatype = KusaCompressedImage.DESCRIPTOR.full_name
    global kusa_pointcloud_datatype
    kusa_pointcloud_datatype = KusaPointCloud.DESCRIPTOR.full_name
    global kusa_localization_datatype
    kusa_localization_datatype = LocalizationEstimate.DESCRIPTOR.full_name
    global kusa_hmi_log_datatype
    kusa_hmi_log_datatype = HmiLog.DESCRIPTOR.full_name
    global kusa_adctrajectory_datatype
    kusa_adctrajectory_datatype = ADCTrajectory.DESCRIPTOR.full_name
    global kusa_PredictionObstacles_datatype
    kusa_PredictionObstacles_datatype = PredictionObstacles.DESCRIPTOR.full_name
    # ========================

    # 新建一个mapping，key为kusa ads topic name，value为数量
    global topic_message_count
    topic_message_count = defaultdict(int)
    # 新建一个camera topic name 到 foxglove topic name的映射
    global camera_topic_map
    camera_topic_map = {}
    camera_topic_map["rt/openads/drives/leopard_camera_front"] = "/hmi/camera_front"
    camera_topic_map["rt/openads/drives/leopard_camera_rear"] = "/hmi/camera_rear"
    camera_topic_map["rt/openads/drives/leopard_camera_left_view_front"] = "/hmi/camera_left_front"
    camera_topic_map["rt/openads/drives/leopard_camera_right_view_front"] = "/hmi/camera_right_front"
    camera_topic_map["rt/openads/drives/leopard_camera_left_view_back"] = "/hmi/camera_left_rear"
    camera_topic_map["rt/openads/drives/leopard_camera_right_view_back"] = "/hmi/camera_right_rear"
    # 新建一个camera frame id 到 foxglove frame id的映射
    global camera_frameid_map
    camera_frameid_map = {}
    camera_frameid_map["leopard_camera_front"] = "camera_front_top"
    camera_frameid_map["leopard_camera_rear"] = "camera_rear"
    camera_frameid_map["leopard_camera_left_view_front"] = "camera_left_front"
    camera_frameid_map["leopard_camera_right_view_front"] = "camera_right_front"
    camera_frameid_map["leopard_camera_left_view_back"] = "camera_left_rear"
    camera_frameid_map["leopard_camera_right_view_back"] = "camera_right_rear"
    # 新建点云topic映射
    global pointcloud_topic_map
    pointcloud_topic_map = {}
    # pointcloud_topic_map["rt/openads/drives/lidar/inno_left_up"] = "/hmi/lidar/inno_left_up"
    # pointcloud_topic_map["rt/openads/drives/lidar/inno_right_up"] = "/hmi/lidar/inno_right_up"
    # pointcloud_topic_map["rt/openads/drives/lidar/inno_left_down"] = "/hmi/lidar/inno_left_down"
    # pointcloud_topic_map["rt/openads/drives/lidar/inno_right_down"] = "/hmi/lidar/inno_right_down"
    
    # 运行cli
    cli()

# 主函数入口
if __name__ == "__main__":
    main()