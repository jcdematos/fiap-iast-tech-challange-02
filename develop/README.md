docker run -it --rm     -v ~/.aws:/home/hadoop/.aws     -v $WORKSPACE_LOCATION:/home/hadoop/workspace/     -e AWS_PROFILE=$PROFILE_NAME     --name glue5_spark_submit public.ecr.aws/glue/aws-glue-libs:5     spark-submit /home/hadoop/workspace/glue_hello_glue.py


