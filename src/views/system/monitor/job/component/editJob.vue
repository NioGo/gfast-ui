<template>
	<div class="system-edit-job-container">
		<el-dialog v-model="isShowDialog" width="720px" :close-on-click-modal="false">
			<template #header>
				<div v-drag="['.system-edit-job-container .el-dialog', '.system-edit-job-container .el-dialog__header']">
					{{ formData.jobId === 0 ? '添加' : '修改' }}定时任务
				</div>
			</template>
			<el-form ref="formRef" :model="formData" :rules="rules" size="small" label-width="110px">
				<el-row :gutter="20">
					<el-col :span="12">
						<el-form-item label="任务名称" prop="jobName">
							<el-input v-model="formData.jobName" placeholder="请输入任务名称" clearable />
						</el-form-item>
					</el-col>
					<el-col :span="12">
						<el-form-item label="任务分组" prop="jobGroup">
							<el-select v-model="formData.jobGroup" placeholder="请选择" style="width: 100%">
								<el-option v-for="dict in sys_job_group" :key="dict.value" :label="dict.label" :value="dict.value" />
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="调用方法" prop="invokeTarget">
							<el-select v-model="formData.invokeTarget" placeholder="请选择" filterable style="width: 100%">
								<el-option v-for="item in funList" :key="item" :label="item" :value="item" />
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="cron表达式" prop="cronExpression">
							<el-input v-model="formData.cronExpression" placeholder="如: 0/10 * * * * * （每10秒）" clearable />
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="传递参数" prop="jobParams">
							<el-input v-model="formData.jobParams" placeholder="多个参数用英文逗号分隔" clearable />
						</el-form-item>
					</el-col>
					<el-col :span="12">
						<el-form-item label="执行策略" prop="misfirePolicy">
							<el-radio-group v-model="formData.misfirePolicy">
								<el-radio v-for="dict in sys_job_policy" :key="dict.value" :label="dict.value">{{ dict.label }}</el-radio>
							</el-radio-group>
						</el-form-item>
					</el-col>
					<el-col :span="12">
						<el-form-item label="是否并发" prop="concurrent">
							<el-radio-group v-model="formData.concurrent">
								<el-radio label="0">允许</el-radio>
								<el-radio label="1">禁止</el-radio>
							</el-radio-group>
						</el-form-item>
					</el-col>
					<el-col :span="12">
						<el-form-item label="任务状态" prop="status">
							<el-radio-group v-model="formData.status">
								<el-radio v-for="dict in sys_job_status" :key="dict.value" :label="dict.value">{{ dict.label }}</el-radio>
							</el-radio-group>
						</el-form-item>
					</el-col>
					<el-col :span="24">
						<el-form-item label="备注" prop="remark">
							<el-input v-model="formData.remark" type="textarea" :rows="2" placeholder="请输入备注" />
						</el-form-item>
					</el-col>
				</el-row>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancel" size="small">取 消</el-button>
					<el-button type="primary" @click="onSubmit" size="small" :loading="loading">
						{{ formData.jobId === 0 ? '新 增' : '修 改' }}
					</el-button>
				</span>
			</template>
		</el-dialog>
	</div>
</template>

<script lang="ts">
import { reactive, toRefs, defineComponent, ref, unref, getCurrentInstance } from 'vue';
import { ElMessage } from 'element-plus';
import { addJob, editJob, getJobFunList } from '/@/api/system/job';

interface DialogRow {
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
}

interface JobState {
	loading: boolean;
	isShowDialog: boolean;
	formData: DialogRow;
	funList: string[];
	rules: object;
	sys_job_group: any[];
	sys_job_status: any[];
	sys_job_policy: any[];
}

export default defineComponent({
	name: 'systemEditJob',
	setup(props, { emit }) {
		const { proxy } = getCurrentInstance() as any;
		const formRef = ref<HTMLElement | null>(null);
		const { sys_job_group, sys_job_status, sys_job_policy } = proxy.useDict('sys_job_group', 'sys_job_status', 'sys_job_policy');
		const state = reactive<JobState>({
			loading: false,
			isShowDialog: false,
			funList: [],
			sys_job_group,
			sys_job_status,
			sys_job_policy,
			formData: {
				jobId: 0,
				jobName: '',
				jobParams: '',
				jobGroup: 'DEFAULT',
				invokeTarget: '',
				cronExpression: '',
				misfirePolicy: '1',
				concurrent: '1',
				status: '1',
				remark: '',
			},
			rules: {
				jobName: [{ required: true, message: '任务名称不能为空', trigger: 'blur' }],
				jobGroup: [{ required: true, message: '任务分组不能为空', trigger: 'change' }],
				invokeTarget: [{ required: true, message: '调用方法不能为空', trigger: 'change' }],
				cronExpression: [{ required: true, message: 'cron表达式不能为空', trigger: 'blur' }],
				misfirePolicy: [{ required: true, message: '执行策略不能为空', trigger: 'change' }],
				concurrent: [{ required: true, message: '是否并发不能为空', trigger: 'change' }],
				status: [{ required: true, message: '任务状态不能为空', trigger: 'change' }],
			},
		});

		const loadFunList = () => {
			getJobFunList().then((res: any) => {
				state.funList = res.data.funList ?? [];
			});
		};

		const openDialog = (row?: DialogRow) => {
			resetForm();
			loadFunList();
			if (row) {
				state.formData = {
					jobId: row.jobId,
					jobName: row.jobName,
					jobParams: row.jobParams || '',
					jobGroup: row.jobGroup,
					invokeTarget: row.invokeTarget,
					cronExpression: row.cronExpression,
					misfirePolicy: String(row.misfirePolicy),
					concurrent: String(row.concurrent),
					status: String(row.status),
					remark: row.remark || '',
				};
			}
			state.isShowDialog = true;
		};

		const closeDialog = () => {
			state.isShowDialog = false;
		};

		const onCancel = () => {
			closeDialog();
		};

		const onSubmit = () => {
			const formWrap = unref(formRef) as any;
			if (!formWrap) return;
			formWrap.validate((valid: boolean) => {
				if (!valid) return;
				state.loading = true;
				const api = state.formData.jobId === 0 ? addJob : editJob;
				api(state.formData)
					.then(() => {
						ElMessage.success(state.formData.jobId === 0 ? '任务添加成功' : '任务修改成功');
						closeDialog();
						emit('getJobList');
					})
					.finally(() => {
						state.loading = false;
					});
			});
		};

		const resetForm = () => {
			state.formData = {
				jobId: 0,
				jobName: '',
				jobParams: '',
				jobGroup: 'DEFAULT',
				invokeTarget: '',
				cronExpression: '',
				misfirePolicy: '1',
				concurrent: '1',
				status: '1',
				remark: '',
			};
		};

		return {
			openDialog,
			closeDialog,
			onCancel,
			onSubmit,
			formRef,
			...toRefs(state),
		};
	},
});
</script>
