import { test, expect } from '@playwright/test';

test.describe('Auth Flow Verification', () => {
  test('should complete the login -> dashboard -> settings -> logout flow', async ({ page }) => {
    // 1. Navigate to the login page
    await page.goto('http://localhost:8088/');

    // 2. Verify login form is visible
    const loginTitle = page.locator('.form-title');
    await expect(loginTitle).toBeVisible();
    await expect(loginTitle).toHaveText('加入我们');

    // 3. Fill in credentials
    // Use the actual labels/placeholders from the code
    await page.locator('el-input[placeholder="请输入用户名"]').fill('admin');
    await page.locator('el-input[placeholder="请输入密码"]').fill('admin');

    // 4. Click "开始使用" (Start using)
    // The button has the text "开始使用" when isLoading is false
    await page.locator('.pill-button').click();

    // 5. Verify Dashboard is visible
    // The content area should now show DashBoard
    const dashboardTitle = page.locator('h2:has-text("数据概览")');
    await expect(dashboardTitle).toBeVisible();

    // 6. Navigate to Settings via Sidebar
    // The sidebar has text "⚙️ 个人设置"
    const settingsLink = page.locator('.sidebar-item').filter({ hasText: '⚙️ 个人设置' });
    await settingsLink.click();

    // 7. Verify Settings page is visible
    const settingsTitle = page.locator('h2:has-text("个人设置")');
    await expect(settingsTitle).toBeVisible();

    // 8. Logout via Sidebar
    // The sidebar has text "🚪 退出登录"
    const logoutLink = page.locator('.sidebar-item').filter({ hasText: '🚪 退出登录' });
    await logoutLink.click();

    // 9. Verify return to login page
    await expect(loginTitle).toBeVisible();
  });
});
