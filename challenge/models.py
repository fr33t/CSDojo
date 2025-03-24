from django.db import models
from django.db.models.signals import post_save
import docker.errors
from CSDojo.utils import docker_client
from CSDojo.settings import CHALLENGES_DIR
from pathlib import Path
import docker

import toml
# traning competions 2 apps
# url static dynamic flag crypt or mics type


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    # class Meta:
    #     verbose_name = "类别"
    #     verbose_name_plural = "类别"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    # class Meta:
    #     verbose_name = "标签"
    #     verbose_name_plural = "标签"


class Challenge(models.Model):
    DIFFICULTY = [
        (0, "简单"),
        (1, "中等"),
        (2, "困难"),
        (3, "疯狂"),
    ]

    title = models.CharField(max_length=3000, verbose_name="题目标题")
    description = models.CharField(max_length=3000, verbose_name="题目描述")
    author = models.CharField(max_length=200, verbose_name="作者")
    related_url = models.CharField(
        max_length=300, verbose_name="相关链接", blank=True, null=True
    )
    is_dockerd = models.BooleanField(default=True, verbose_name="是否需要docker运行")
    # toml
    config_dir = models.CharField(
        max_length=300,
        verbose_name="启动文件具体位置 /var/challenges/ ",
        null=True,
        blank=True,
    )

    difficulty = models.IntegerField(
        choices=DIFFICULTY, default=0, verbose_name="题目难度"
    )

    tags = models.ManyToManyField(
        Tag, blank=True, verbose_name="标签", related_name="challenges"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="类别",
        related_name="challenges",
    )

    visibility = models.BooleanField(default=False, verbose_name="可见性")
    created_at = models.DateField(verbose_name="添加日期", auto_now_add=True)

    image_existed = models.BooleanField(
        default=False, verbose_name="镜像是否存在， 是否可以启动"
    )

    def __str__(self):
        return self.title

    # class Meta:
    #     verbose_name = "题目"
    #     verbose_name_plural = "题库"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "related_url": self.related_url,
            "category": self.category.name,
            "tags": [tag.name for tag in self.tags.all()],
        }

    def build_image(self):
        data = self.from_toml()

        try:
            _ = docker_client.images.get(data["docker_image"])

        except KeyError:
            raise

        except docker.errors.ImageNotFound as e:
            # pull 拉下来
            try:
                _ = docker_client.images.pull(data["docker_image"])

            except Exception as e:
                # dockefile 存在 构建，
                dockerfile_path = Path(CHALLENGES_DIR) / self.config_dir / "Dockerfile"
                context_path = Path(CHALLENGES_DIR) / self.config_dir
                if dockerfile_path.exists():
                    try:
                        docker_client.images.build(
                            path=str(context_path),
                            dockerfile=str(dockerfile_path),
                            tag=data["docker_image"],
                            rm=True,
                        )
                        return True

                    except Exception as e:
                        raise e
                raise e
            raise e

    def from_toml(self):
        data = {}
        path = Path(CHALLENGES_DIR) / self.config_dir / "CSDojo.toml"

        with open(path, "r") as f:
            config = toml.load(f)
        try:
            flag_config = config["flag"]
            docker_config = config["docker"]
            data["training_name"] = config["training_name"]
            data["docker_image"] = docker_config["docker_image"]
            data["port"] = docker_config["port"]
            data["static_flag"] = flag_config["static_flag"]
            data["is_nc"] = flag_config["is_nc"]
        except KeyError:
            raise
        data["cpu_limit"] = docker_config.get("cpu_limit", 1)
        data["memory_limit"] = docker_config.get("memory_limit", 64)
        data["disk_limit"] = docker_config.get("disk_limit", 256)
        data["privileged"] = docker_config.get("privileged", False)
        data["is_dynamic"] = flag_config.get("is_dynamic", True)
        return data
