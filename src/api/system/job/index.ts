import request from '/@/utils/request';

export function getJobList(query: Object) {
	return request({
		url: '/api/v1/system/job/list',
		method: 'get',
		params: query,
	});
}

export function getJob(jobId: number) {
	return request({
		url: '/api/v1/system/job/get',
		method: 'get',
		params: { jobId },
	});
}

export function addJob(data: object) {
	return request({
		url: '/api/v1/system/job/add',
		method: 'post',
		data: data,
	});
}

export function editJob(data: object) {
	return request({
		url: '/api/v1/system/job/edit',
		method: 'put',
		data: data,
	});
}

export function deleteJob(jobIds: number[]) {
	return request({
		url: '/api/v1/system/job/delete',
		method: 'delete',
		data: { jobIds },
	});
}

export function changeJobStatus(data: object) {
	return request({
		url: '/api/v1/system/job/changeStatus',
		method: 'put',
		data: data,
	});
}

export function runJob(jobId: number) {
	return request({
		url: '/api/v1/system/job/run',
		method: 'put',
		data: { jobId },
	});
}

export function getJobFunList() {
	return request({
		url: '/api/v1/system/job/funList',
		method: 'get',
	});
}

export function getJobLogList(query: Object) {
	return request({
		url: '/api/v1/system/job/logList',
		method: 'get',
		params: query,
	});
}

export function deleteJobLog(ids: number[]) {
	return request({
		url: '/api/v1/system/job/logDelete',
		method: 'delete',
		data: { ids },
	});
}

export function clearJobLog() {
	return request({
		url: '/api/v1/system/job/logClear',
		method: 'delete',
	});
}
