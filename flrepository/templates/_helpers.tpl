{{/*
Expand the name of the chart.
*/}}
{{- define "enabler.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "enabler.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "enabler.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Name of the component flrepository.
*/}}
{{- define "flrepository.name" -}}
{{ include "enabler.name" . }}-flrepository
{{- end }}

{{/*
Component flrepository labels
*/}}
{{- define "flrepository.labels" -}}
helm.sh/chart: {{ include "enabler.chart" . }}
{{ include "flrepository.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Component flrepository selector labels
*/}}
{{- define "flrepository.selectorLabels" -}}
app.kubernetes.io/name: {{ include "enabler.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
enabler: {{ .Chart.Name }}
component: {{ .Values.flrepository.name }}
isMainInterface: "yes"
tier: {{ .Values.flrepository.tier}}
{{- end }}

{{/*
Name of the component repositorydb.
*/}}
{{- define "repositorydb.name" -}}
{{ include "enabler.name" . }}-repositorydb
{{- end }}

{{/*
Component repositorydb labels
*/}}
{{- define "repositorydb.labels" -}}
helm.sh/chart: {{ include "enabler.chart" . }}
{{ include "repositorydb.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Component repositorydb selector labels
*/}}
{{- define "repositorydb.selectorLabels" -}}
app.kubernetes.io/name: {{ include "enabler.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
enabler: {{ .Chart.Name }}
component: {{ .Values.repositorydb.name }}
isMainInterface: "no"
tier: {{ .Values.repositorydb.tier}}
{{- end }}

