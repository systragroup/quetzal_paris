# docker build need to be run from folder containing model and quetzal library
FROM public.ecr.aws/lambda/python:3.8.2023.01.11.07

# Install dependancies and add them to paths
COPY ./quetzal_paris/requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
ENV PATH="${PATH}:${LAMBDA_TASK_ROOT}/bin"
ENV PYTHONPATH="${PYTHONPATH}:${LAMBDA_TASK_ROOT}"

# Copy src code
COPY ./quetzal ${LAMBDA_TASK_ROOT}/quetzal
COPY ./quetzal_paris/main.py ${LAMBDA_TASK_ROOT}
COPY ./quetzal_paris ${LAMBDA_TASK_ROOT}

# Entrypoint
CMD ["main.handler"]