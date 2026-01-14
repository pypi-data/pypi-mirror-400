from deepomatic.oef.configs.config_utils import DataType, ModelConfig

from ..utils import fixed_shape_resizer
from ..backbones import Backbones as bb

THREE_STEPS_POLICY = {
    "manual_step_learning_rate": {
        "schedule": [
            {
                "learning_rate_factor": 0.1,
                "step_pct": 0.33
            },
            {
                "learning_rate_factor": 0.01,
                "step_pct": 0.66
            }
        ],
    }
}

ONE_CYCLE_POLICY = {'one_cycle_learning_rate': {'cycle_steps': 2}}

MOMENTUM_OPTIMIZER = {'momentum_optimizer': {}}
NADAM_OPTIMIZER = {'nadam_optimizer': {}}

yolo_v2 = ModelConfig(
    display_name='YOLO v2',
    meta_arch='yolo_v2',
    args={
        'trainer': {
            'batch_size': 64,
        },
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(416, 416),
            'data_augmentation_options': [],
        },
        '@meta_arch.parameters': {
            'subdivisions': 16,
            'classification_loss': {'weighted_softmax': {'logit_scale': 1.0}}
        },

    },
)
yolo_v2.add_backbone(
    bb.DARKNET_19, args={'trainer': {
        'initial_learning_rate': 0.002,
        'optimizer': MOMENTUM_OPTIMIZER,
        'learning_rate_policy': THREE_STEPS_POLICY
    }},
    pretrained_parameters={DataType.NATURAL_RGB: 'darknet/natural_rgb/darknet19-yolo-voc2007.weights'}
)

yolo_v3 = ModelConfig(
    display_name='YOLO v3',
    meta_arch='yolo_v3',
    args={
        'trainer': {
            'batch_size': 64,
        },
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(416, 416),
            'data_augmentation_options': [],
        },
        '@meta_arch.parameters': {
            'subdivisions': 32,
            'classification_loss': {'weighted_sigmoid': {}}
        },
    },
)
yolo_v3.add_backbone(
    bb.DARKNET_53, args={'trainer': {
        'initial_learning_rate': 0.01,
        'optimizer': MOMENTUM_OPTIMIZER,
        'learning_rate_policy': THREE_STEPS_POLICY
    }},
    pretrained_parameters={DataType.NATURAL_RGB: 'darknet/natural_rgb/darknet53-yolo-imagenet2012.weights'}
)

yolo_v3_keras = ModelConfig(
    display_name='YOLO v3 Keras',
    meta_arch='yolo_v3_keras',
    args={
        'trainer': {
            'batch_size': 16,
        },
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(416, 416),
            'data_augmentation_options': [],
        },
        '@meta_arch.parameters': {
            'subdivisions': 32,  # FIXME this is not used in the keras model
            'classification_loss': {'weighted_softmax': {}}
        },
    },
)

yolo_v3_keras.add_backbone(
    bb.DARKNET_53,
    args={
        'trainer': {
            'initial_learning_rate': 1e-4,
            'optimizer': {'momentum_optimizer': {}},
            'learning_rate_policy': ONE_CYCLE_POLICY
        }
    },
    switch_args=[
        {
            "field": "trainer.optimizer.optimizer",
            "triggering_value": "momentum_optimizer",
            "target_value": {
                "trainer": {
                    "initial_learning_rate": 1e-4,
                    "learning_rate_policy": ONE_CYCLE_POLICY,
                }
            },
        },
        {
            "field": "trainer.optimizer.optimizer",
            "triggering_value": "rms_prop_optimizer",
            "target_value": {
                "trainer": {
                    "initial_learning_rate": 1e-4,
                    "learning_rate_policy": ONE_CYCLE_POLICY,
                }
            },
        },
        {
            "field": "trainer.optimizer.optimizer",
            "triggering_value": "adam_optimizer",
            "target_value": {
                "trainer": {
                    "initial_learning_rate": 2e-5,
                    "learning_rate_policy": ONE_CYCLE_POLICY,
                }
            },
        },
        {
            "field": "trainer.optimizer.optimizer",
            "triggering_value": "nadam_optimizer",
            "target_value": {
                "trainer": {
                    "initial_learning_rate": 2e-5,
                    "learning_rate_policy": ONE_CYCLE_POLICY,
                }
            },
        },
        {
            "field": "trainer.optimizer.optimizer",
            "triggering_value": "rectified_adam_optimizer",
            "target_value": {
                "trainer": {
                    "initial_learning_rate": 2e-5,
                    "learning_rate_policy": ONE_CYCLE_POLICY,
                }
            },
        },
    ],
    pretrained_parameters={
        DataType.NATURAL_RGB: 'keras/natural_rgb/yolo_v3_full.tar.gz'
    }
)

yolo_v3_spp = ModelConfig(
    display_name='YOLO v3 SPP',
    meta_arch='yolo_v3_spp',
    args={
        'trainer': {
            'batch_size': 64,
        },
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(608, 608),
            'data_augmentation_options': [],
        },
        '@meta_arch.parameters': {
            'subdivisions': 16,
            'classification_loss': {'weighted_sigmoid': {}}
        },
    },
)
yolo_v3_spp.add_backbone(
    bb.DARKNET_53,
    args={'trainer': {
        'initial_learning_rate': 0.001,
        'optimizer': MOMENTUM_OPTIMIZER,
        'learning_rate_policy': THREE_STEPS_POLICY,
    }},
    pretrained_parameters={DataType.NATURAL_RGB: 'darknet/natural_rgb/darknet53-yolo_v3_spp_608-coco.weights'}
)


yolo_v8 = ModelConfig(
    display_name='YOLO v8',
    meta_arch='yolo_v8',
    args={
        'trainer': {
            'optimizer': {'nadam_optimizer': {}},
            'learning_rate_policy': {'constant_learning_rate': {}},
        },
        '@model.backbone.input': {
            'image_resizer': fixed_shape_resizer(640, 640),
            'data_augmentation_options': [{'random_horizontal_flip': {'keypoint_flip_permutation': []}}],
        },
        '@meta_arch': {
        },
    },
)
yolo_v8.add_backbone(
    bb.YOLOV8_N,
    args={
        'trainer': {
            'batch_size': 16,
            'initial_learning_rate': 0.00003,
        }
    },
    pretrained_parameters={DataType.NATURAL_RGB: 'torch/natural_rgb/ultralytics-20230102-yolov8n.ckpt.pt'}
)
yolo_v8.add_backbone(
    bb.YOLOV8_S,
    args={
        'trainer': {
            'batch_size': 16,
            'initial_learning_rate': 0.00003,
        }
    },
    pretrained_parameters={DataType.NATURAL_RGB: 'torch/natural_rgb/ultralytics-20230102-yolov8s.ckpt.pt'}
)
yolo_v8.add_backbone(
    bb.YOLOV8_M,
    args={
        'trainer': {
            'batch_size': 16,
            'initial_learning_rate': 0.00003,
        }
    },
    pretrained_parameters={DataType.NATURAL_RGB: 'torch/natural_rgb/ultralytics-20230102-yolov8m.ckpt.pt'}
)
yolo_v8.add_backbone(
    bb.YOLOV8_L,
    args={
        'trainer': {
            'batch_size': 8,
            'initial_learning_rate': 0.00001,
        }
    },
    pretrained_parameters={DataType.NATURAL_RGB: 'torch/natural_rgb/ultralytics-20230102-yolov8l.ckpt.pt'}
)
yolo_v8.add_backbone(
    bb.YOLOV8_X,
    args={
        'trainer': {
            'batch_size': 8,
            'initial_learning_rate': 0.00001,
        }
    },
    pretrained_parameters={DataType.NATURAL_RGB: 'torch/natural_rgb/ultralytics-20230102-yolov8x.ckpt.pt'}
)


configs = [yolo_v2, yolo_v3, yolo_v3_keras, yolo_v3_spp, yolo_v8]
