# Makefile for microservices of ML Prediction service

tag := $(if $(tag),$(tag),latest)

build-server:
	docker build -f server/Dockerfile . -t ml_pred_server:$(tag)

build-inference-engine:
	docker build -f inference_engine/Dockerfile . -t ml_pred_inference_engine:$(tag)

