<template>
	<div class="system-job-container">
		<el-card shadow="hover">
			<div class="system-job-search mb15">
				<el-form :inline="true" :model="tableData.param" size="small">
					<el-form-item label="任务名称">
						<el-input
							v-model="tableData.param.jobName"
							placeholder="请输入任务名称"
							style="width: 180px"
							clearable
							@keyup.enter="jobList"
						/>
					</el-form-item>
					<el-form-item label="任务分组">
						<el-select v-model="tableData.param.jobGroup" placeholder="请选择" clearable style="width: 180px">
							<el-option v-for="dict in sys_job_group" :key="dict.value" :label="dict.label" :value="dict.value" />
						</el-select>
					</el-form-item>
					<el-form-item label="任务状态">
						<el-select v-model="tableData.param.status" placeholder="请选择" clearable style="width: 180px">
							<el-option v-for="dict in sys_job_status" :key="dict.value" :label="dict.label" :value="dict.value" />
						</el-select>
					</el-form-item>
					<el-form-item>
						<el-button type="primary" size="small" @click="jobList">
							<el-icon><ele-Search /></el-icon>查询
						</el-button>
						<el-button size="small" @click="resetQuery">
							<el-icon><ele-Refresh /></el-icon>重置
						</el-button>
						<el-button type="success" size="small" class="ml10" v-auth="'api/v1/system/job/add'" @click="onOpenAdd">
							<el-icon><ele-FolderAdd /></el-icon>新增
						</el-button>
						<el-button type="danger" size="small" class="ml10" v-auth="'api/v1/system/job/delete'" @click="onRowDel(null)">
							<el-icon><ele-Delete /></el-icon>删除
						</el-button>
						<el-button type="warning" size="small" class="ml10" v-auth="'api/v1/system/job/logList'" @click="onOpenLog()">
							<el-icon><ele-DocumentCopy /></el-icon>日志
						</el-button>
					</el-form-item>
				</el-form>
			</div>

			<el-table
				border
				v-loading="tableData.loading"
				:data="tableData.data"
				style="width: 100%"
				@selection-change="handleSelectionChange"
				@sort-change="onSortChange"
			>
				<el-table-column type="selection" width="55" align="center" />
				<el-table-column prop="jobId" label="任务编号" width="90" align="center" sortable="custom" />
				<el-table-column prop="jobName" label="任务名称" min-width="120" show-overflow-tooltip sortable="custom" />
				<el-table-column prop="jobGroup" label="任务分组" width="100" align="center">
					<template #default="scope">
						{{ proxy.selectDictLabel(sys_job_group, scope.row.jobGroup) }}
					</template>
				</el-table-column>
				<el-table-column prop="invokeTarget" label="调用方法" min-width="120" show-overflow-tooltip />
				<el-table-column prop="cronExpression" label="cron表达式" min-width="140" show-overflow-tooltip />
				<el-table-column prop="misfirePolicy" label="执行策略" width="100" align="center">
					<template #default="scope">
						{{ proxy.selectDictLabel(sys_job_policy, scope.row.misfirePolicy) }}
					</template>
				</el-table-column>
				<el-table-column prop="status" label="状态" width="90" align="center" sortable="custom">
					<template #default="scope">
						<el-tag type="success" v-if="String(scope.row.status) === '0'">正常</el-tag>
						<el-tag type="info" v-else>暂停</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="createdAt" label="创建时间" width="170" align="center" sortable="custom" />
				<el-table-column label="操作" width="280" align="center" fixed="right">
					<template #default="scope">
						<el-button size="small" text type="primary" v-auth="'api/v1/system/job/edit'" @click="onOpenEdit(scope.row)">修改</el-button>
						<el-button
							size="small"
							text
							type="primary"
							v-auth="'api/v1/system/job/changeStatus'"
							@click="onChangeStatus(scope.row)"
						>
							{{ String(scope.row.status) === '0' ? '暂停' : '启动' }}
						</el-button>
						<el-button size="small" text type="primary" v-auth="'api/v1/system/job/run'" @click="onRun(scope.row)">执行一次</el-button>
						<el-button size="small" text type="primary" v-auth="'api/v1/system/job/logList'" @click="onOpenLog(scope.row)">日志</el-button>
						<el-button size="small" text type="primary" v-auth="'api/v1/system/job/delete'" @click="onRowDel(scope.row)">删除</el-button>
					</template>
				</el-table-column>
			</el-table>

			<pagination
				v-show="tableData.total > 0"
				:total="tableData.total"
				v-model:page="tableData.param.pageNum"
				v-model:limit="tableData.param.pageSize"
				@pagination="jobList"
			/>
		</el-card>

		<EditJob ref="editJobRef" @getJobList="jobList" />
		<JobLog ref="jobLogRef" />
	</div>
</template>

<script lang="ts">
import { defineComponent, getCurrentInstance, onMounted, reactive, ref, toRaw, toRefs } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import EditJob from '/@/views/system/monitor/job/component/editJob.vue';
import JobLog from '/@/views/system/monitor/job/component/jobLog.vue';
import { changeJobStatus, deleteJob, getJobList, runJob } from '/@/api/system/job';

interface TableData {
	jobId: number;
	jobName: string;
	jobParams: string;
	jobGroup: string;
	invokeTarget: string;
	cronExpression: string;
	misfirePolicy: string;
	concurrent: string;
	status: string;
	remark: string;
	createdAt: string;
}

export default defineComponent({
	name: 'apiV1SystemJobList',
	components: { EditJob, JobLog },
	setup() {
		const { proxy } = getCurrentInstance() as any;
		const editJobRef = ref();
		const jobLogRef = ref();
		const { sys_job_group, sys_job_status, sys_job_policy } = proxy.useDict('sys_job_group', 'sys_job_status', 'sys_job_policy');
		const state = reactive({
			ids: [] as number[],
			sys_job_group,
			sys_job_status,
			sys_job_policy,
			tableData: {
				data: [] as TableData[],
				total: 0,
				loading: false,
				param: {
					jobName: '',
					jobGroup: '',
					status: '',
					pageNum: 1,
					pageSize: 20,
					orderBy: 'job_id desc',
				},
			},
		});

		const jobList = () => {
			state.tableData.loading = true;
			getJobList(state.tableData.param)
				.then((res: any) => {
					state.tableData.data = res.data.jobList ?? [];
					state.tableData.total = res.data.total;
				})
				.finally(() => {
					state.tableData.loading = false;
				});
		};

		const resetQuery = () => {
			state.tableData.param.jobName = '';
			state.tableData.param.jobGroup = '';
			state.tableData.param.status = '';
			state.tableData.param.pageNum = 1;
			state.tableData.param.orderBy = 'job_id desc';
			jobList();
		};

		const onOpenAdd = () => {
			editJobRef.value.openDialog();
		};

		const onOpenEdit = (row: TableData) => {
			editJobRef.value.openDialog(toRaw(row));
		};

		const onOpenLog = (row?: TableData) => {
			jobLogRef.value.openDialog(row ? { jobId: row.jobId, jobName: row.jobName } : undefined);
		};

		const onRowDel = (row: TableData | null) => {
			let msg = '你确定要删除所选任务？';
			let ids: number[] = [];
			if (row) {
				msg = `此操作将永久删除任务：“${row.jobName}”，是否继续?`;
				ids = [row.jobId];
			} else {
				ids = state.ids;
			}
			if (!ids.length) {
				ElMessage.error('请选择要删除的数据。');
				return;
			}
			ElMessageBox.confirm(msg, '提示', {
				confirmButtonText: '确认',
				cancelButtonText: '取消',
				type: 'warning',
			})
				.then(() => {
					deleteJob(ids).then(() => {
						ElMessage.success('删除成功');
						jobList();
					});
				})
				.catch(() => {});
		};

		const onChangeStatus = (row: TableData) => {
			const status = String(row.status) === '0' ? '1' : '0';
			const text = status === '0' ? '启动' : '暂停';
			ElMessageBox.confirm(`确认要${text}任务“${row.jobName}”吗？`, '提示', { type: 'warning' })
				.then(() => {
					changeJobStatus({ jobId: row.jobId, status }).then(() => {
						ElMessage.success(`${text}成功`);
						jobList();
					});
				})
				.catch(() => {});
		};

		const onRun = (row: TableData) => {
			ElMessageBox.confirm(`确认要立即执行一次任务“${row.jobName}”吗？`, '提示', { type: 'warning' })
				.then(() => {
					runJob(row.jobId).then(() => {
						ElMessage.success('执行指令已下发');
					});
				})
				.catch(() => {});
		};

		const handleSelectionChange = (selection: TableData[]) => {
			state.ids = selection.map((item) => item.jobId);
		};

		const onSortChange = ({ prop, order }: { prop: string; order: string | null }) => {
			if (!order) {
				state.tableData.param.orderBy = 'job_id desc';
			} else {
				const col = prop.replace(/([A-Z])/g, '_$1').toLowerCase();
				state.tableData.param.orderBy = `${col} ${order === 'ascending' ? 'asc' : 'desc'}`;
			}
			jobList();
		};

		onMounted(() => {
			jobList();
		});

		return {
			proxy,
			editJobRef,
			jobLogRef,
			jobList,
			resetQuery,
			onOpenAdd,
			onOpenEdit,
			onOpenLog,
			onRowDel,
			onChangeStatus,
			onRun,
			handleSelectionChange,
			onSortChange,
			...toRefs(state),
		};
	},
});
</script>
