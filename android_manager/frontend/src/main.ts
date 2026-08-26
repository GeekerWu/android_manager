import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 导入我们刚刚创建的模拟路由文件
import * as ElementPlus from 'element-plus';
import 'element-plus/dist/index.css'
import { ElMessage } from 'element-plus';


// 1. 创建路由实例并挂载到应用实例
const app = createApp(App);

app.use(router);
app.use(ElementPlus);
app.config.globalProperties.$message = ElMessage;

// 2. 挂载应用到 DOM 元素
app.mount('#app');
