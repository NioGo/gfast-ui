<template>
	<div class="system-job-log-container">
		<el-dialog v-model="isShowDialog" width="960px" title="调度日志" :close-on-click-modal="false" destroy-on-close>
			<div class="mb15">
				<el-form :model="tableData.param" :inline="true" size="small">
					<el-form-item label="任务名称">
						<el-input v-model="tableData.param.jobName" placeholder="请输入任务名称" clearable style="width: 180px" />
					</el-form-item>
					<el-form-item label="调用方法">
						<el-input v-model="tableData.param.targetName" placeholder="请输入调用方法" clearable style="width: 180px" />
					</el-form-item>
					<el-form-item label="执行状态">
						<el-select v-model="tableData.param.status" placeholder="请选择" clearable style="width: 180px">
							<el-option label="成功" value="0" />
							<el-option label="失败" value="1" />
						</el-select>
					</el-form-item>
					<el-form-item>
						<el-button type="primary" @click="logList"><el-icon><ele-Search /></el-icon>搜索</el-button>
						<el-button
							type="danger"
							:disabled="ids.length === 0"
							v-auth="'api/v1/system/job/logDelete'"
							@click="onDelete(null)"
						>
							<el-icon><ele-Delete /></el-icon>删除
						</el-button>
						<el-button type="danger" plain v-auth="'api/v1/system/job/logClear'" @click="onClear">
							<el-icon><ele-Delete /></el-icon>清空
						</el-button>
					</el-form-item>
				</el-form>
			</div>
			<el-table border v-loading="tableData.loading" :data="tableData.data" @selection-change="handleSelectionChange" max-height="420">
				<el-table-column type="selection" width="50" align="center" />
				<el-table-column prop="id" label="日志编号" width="90" align="center" />
				<el-table-column prop="jobName" label="任务名称" min-width="120" show-overflow-tooltip />
				<el-table-column prop="targetName" label="调用方法" min-width="120" show-overflow-tooltip />
				<el-table-column prop="status" label="状态" width="80" align="center">
					<template #default="scope">
						<el-tag type="success" v-if="scope.row.status === '0'">成功</el-tag>
						<el-tag type="danger" v-else>失败</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="result" label="执行结果" min-width="180" show-overflow-tooltip />
				<el-table-column prop="createdAt" label="执行时间" width="170" align="center" />
				<el-table-column label="操作" width="80" align="center" fixed="right">
					<template #default="scope">
						<el-button size="small" text type="primary" @click="onDetail(scope.row)">详情</el-button>
					</template>
				</el-table-column>
			</el-table>
			<pagination
				v-show="tableData.total > 0"
				:total="tableData.total"
				v-model:page="tableData.param.pageNum"
				v-model:limit="tableData.param.pageSize"
				@pagination="logList"
			/>
		</el-dialog>

		<el-dialog v-model="detailVisible" title="日志详情" width="620px" append-to-body>
			<el-descriptions :column="1" border>
				<el-descriptions-item label="日志编号">{{ detail.id }}</el-descriptions-item>
				<el-descriptions-item label="任务名称">{{ detail.jobName }}</el-descriptions-item>
				<el-descriptions-item label="调用方法">{{ detail.targetName }}</el-descriptions-item>
				<el-descriptions-item label="执行状态">
					<el-tag type="success" v-if="detail.status === '0'">成功</el-tag>
					<el-tag type="danger" v-else>失败</el-tag>
				</el-descriptions-item>
				<el-descriptions-item label="执行时间">{{ detail.createdAt }}</el-descriptions-item>
				<el-descriptions-item label="执行结果">
					<pre class="job-log-result">{{ detail.result }}</pre>
				</el-descriptions-item>
			</el-descriptions>
		</el-dialog>
	</div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { clearJobLog, deleteJobLog, getJobLogList } from '/@/api/system/job';

interface LogRow {
	id: number;
	jobId: number;
	jobName: string;
	targetName: string;
	status: string;
	result: string;
	createdAt: string;
}

export default defineComponent({
	name: 'systemJobLog',
	setup() {
		const state = reactive({
			isShowDialog: false,
			detailVisible: false,
			ids: [] as number[],
			detail: {} as LogRow,
			tableData: {
				data: [] as LogRow[],
				total: 0,
				loading: false,
				param: {
					jobId: 0 as number,
					jobName: '',
					targetName: '',
					status: '',
					pageNum: 1,
					pageSize: 20,
					orderBy: 'id desc',
				},
			},
		});

		const openDialog = (row?: { jobId?: number; jobName?: string }) => {
			state.tableData.param.pageNum = 1;
			state.tableData.param.jobId = row?.jobId ?? 0;
			state.tableData.param.jobName = row?.jobName ?? '';
			state.tableData.param.targetName = '';
			state.tableData.param.status = '';
			state.isShowDialog = true;
			logList();
		};

		const logList = () => {
			state.tableData.loading = true;
			getJobLogList(state.tableData.param)
				.then((res: any) => {
					state.tableData.data = res.data.list ?? [];
					state.tableData.total = res.data.total;
				})
				.finally(() => {
					state.tableData.loading = false;
				});
		};

		const handleSelectionChange = (selection: LogRow[]) => {
			state.ids = selection.map((item) => item.id);
		};

		const onDelete = (row: LogRow | null) => {
			const ids = row ? [row.id] : state.ids;
			if (!ids.length) {
				ElMessage.error('请选择要删除的日志');
				return;
			}
			ElMessageBox.confirm('确认删除所选调度日志？', '提示', { type: 'warning' })
				.then(() => {
					deleteJobLog(ids).then(() => {
						ElMessage.success('删除成功');
						logList();
					});
				})
				.catch(() => {});
		};

		const onClear = () => {
			ElMessageBox.confirm('确认清空全部调度日志？此操作不可恢复', '提示', { type: 'warning' })
				.then(() => {
					clearJobLog().then(() => {
						ElMessage.success('清空成功');
						logList();
					});
				})
				.catch(() => {});
		};

		const onDetail = (row: LogRow) => {
			state.detail = row;
			state.detailVisible = true;
		};

		return {
			openDialog,
			logList,
			handleSelectionChange,
			onDelete,
			onClear,
			onDetail,
			...toRefs(state),
		};
	},
});
</script>

<style scoped>
.job-log-result {
	margin: 0;
	white-space: pre-wrap;
	word-break: break-all;
	font-family: inherit;
}
</style>
