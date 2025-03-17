from django.db import models


# traning competions 2 apps
# url static dynamic flag crypt or mics type


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Challenge(models.Model):
    RUN_TYPE = [
        (0, "Dockerfile"),
        (1, "DockerImage"),
        (2, "URL"),
    ]

    FLAG_TYPE = [
        (0, "静态"),
        (1, "动态"),
    ]

    title = models.CharField(max_length=3000, verbose_name="题目标题")
    description = models.CharField(max_length=3000, verbose_name="题目描述")
    author = models.CharField(max_length=200, verbose_name="作者")
    related_url = models.CharField(max_length=300, verbose_name="相关链接")
    visibility = models.BooleanField(default=False, verbose_name="可见性")
    created_at = models.DateField(verbose_name="添加日期")

    flag_type = models.IntegerField(choices=FLAG_TYPE, verbose_name="Flag类型")
    run_type = models.IntegerField(choices=RUN_TYPE, verbose_name="启动文件类型")

    run_url = models.CharField(
        max_length=300, verbose_name="启动文件具体位置", blank=True
    )

    tags = models.ManyToManyField(Tag, blank=True, verbose_name="标签")
    categories = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="类别"
    )

    def __str__(self):
        return self.title
