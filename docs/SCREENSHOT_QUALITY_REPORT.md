# Screenshot Quality Report

This report is generated from automated image checks to reject blank, uniform, or obviously incomplete screenshots.

## Active Rules

- `min_width`: `600`
- `min_height`: `350`
- `min_unique_colors`: `24`
- `min_stddev`: `8.0`
- `max_dominant_ratio`: `0.995`

## Screenshot Audit

- `PASS` `D:\Projects\Services\project-validation\screenshots\application\frontend-dashboard.png`: image looks populated (size=3840x2160, colors=396, stddev=12.11, dominant=0.1072)
- `PASS` `D:\Projects\Services\project-validation\screenshots\application\frontend-login.png`: image looks populated (size=3840x2160, colors=421, stddev=25.24, dominant=0.0776)
- `PASS` `D:\Projects\Services\project-validation\screenshots\application\frontend-signup-success.png`: image looks populated (size=3840x2160, colors=439, stddev=25.34, dominant=0.075)
- `PASS` `D:\Projects\Services\project-validation\screenshots\application\frontend-signup.png`: image looks populated (size=3840x2160, colors=432, stddev=25.11, dominant=0.071)
- `PASS` `D:\Projects\Services\project-validation\screenshots\application\order-ledger.png`: image looks populated (size=3840x2160, colors=483, stddev=13.08, dominant=0.1289)
- `PASS` `D:\Projects\Services\project-validation\screenshots\application\product-form.png`: image looks populated (size=3840x2160, colors=403, stddev=12.46, dominant=0.1072)
- `PASS` `D:\Projects\Services\project-validation\screenshots\application\product-list.png`: image looks populated (size=3840x2160, colors=448, stddev=12.68, dominant=0.1472)
- `PASS` `D:\Projects\Services\project-validation\screenshots\application\user-activity.png`: image looks populated (size=3840x2160, colors=483, stddev=13.08, dominant=0.1289)
- `PASS` `D:\Projects\Services\project-validation\screenshots\ci\frontend-quality-job.png`: image looks populated (size=1600x1345, colors=321, stddev=45.37, dominant=0.4502)
- `PASS` `D:\Projects\Services\project-validation\screenshots\ci\frontend-quality-summary.png`: image looks populated (size=1600x1200, colors=367, stddev=48.98, dominant=0.4622)
- `PASS` `D:\Projects\Services\project-validation\screenshots\ci\infra-quality-summary.png`: image looks populated (size=1600x1200, colors=365, stddev=48.98, dominant=0.4597)
- `PASS` `D:\Projects\Services\project-validation\screenshots\ci\kafka-quality-summary.png`: image looks populated (size=1600x1200, colors=370, stddev=48.98, dominant=0.4565)
- `PASS` `D:\Projects\Services\project-validation\screenshots\ci\order-quality-summary.png`: image looks populated (size=1600x1200, colors=374, stddev=48.99, dominant=0.4607)
- `PASS` `D:\Projects\Services\project-validation\screenshots\ci\product-quality-summary.png`: image looks populated (size=1600x1200, colors=374, stddev=48.99, dominant=0.4607)
- `PASS` `D:\Projects\Services\project-validation\screenshots\ci\project-validation-quality-summary.png`: image looks populated (size=1600x1200, colors=373, stddev=48.98, dominant=0.4597)
- `PASS` `D:\Projects\Services\project-validation\screenshots\deployment\application-home-proof.png`: image looks populated (size=3840x2160, colors=421, stddev=25.24, dominant=0.0776)
- `PASS` `D:\Projects\Services\project-validation\screenshots\deployment\argocd-deployment-app.png`: image looks populated (size=3840x2160, colors=761, stddev=68.39, dominant=0.4592)
- `PASS` `D:\Projects\Services\project-validation\screenshots\deployment\deployment-result-proof.png`: image looks populated (size=3840x2160, colors=331, stddev=51.6, dominant=0.3906)
- `PASS` `D:\Projects\Services\project-validation\screenshots\deployment\github-actions-run-summary.png`: image looks populated (size=3840x2160, colors=343, stddev=51.61, dominant=0.3914)
- `PASS` `D:\Projects\Services\project-validation\screenshots\deployment\github-actions-runner-proof.png`: image looks populated (size=3840x2160, colors=299, stddev=50.88, dominant=0.4756)
- `PASS` `D:\Projects\Services\project-validation\screenshots\deployment\gitops-commit-proof.png`: image looks populated (size=3840x2160, colors=419, stddev=51.83, dominant=0.4399)
- `PASS` `D:\Projects\Services\project-validation\screenshots\deployment\latest-tags-metadata-proof.png`: image looks populated (size=3840x2160, colors=409, stddev=51.83, dominant=0.563)
- `PASS` `D:\Projects\Services\project-validation\screenshots\deployment\service-ci-latest-tag-publish.png`: image looks populated (size=3840x2160, colors=369, stddev=51.58, dominant=0.3936)
- `PASS` `D:\Projects\Services\project-validation\screenshots\gitops\argocd-app-detail.png`: image looks populated (size=3840x2160, colors=761, stddev=68.39, dominant=0.4592)
- `PASS` `D:\Projects\Services\project-validation\screenshots\gitops\argocd-app-list.png`: image looks populated (size=3840x2160, colors=899, stddev=72.87, dominant=0.1963)
- `PASS` `D:\Projects\Services\project-validation\screenshots\gitops\argocd-login.png`: image looks populated (size=3840x2160, colors=899, stddev=72.87, dominant=0.1963)
- `PASS` `D:\Projects\Services\project-validation\screenshots\messaging\kafka-dashboard.png`: image looks populated (size=3840x2160, colors=235, stddev=9.2, dominant=0.3965)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\dashboard-frontend.png`: image looks populated (size=3840x2160, colors=380, stddev=21.87, dominant=0.395)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\dashboard-kafka.png`: image looks populated (size=3840x2160, colors=235, stddev=9.2, dominant=0.3965)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\dashboard-logs.png`: image looks populated (size=3840x2160, colors=367, stddev=19.59, dominant=0.3889)
- `FAIL` `D:\Projects\Services\project-validation\screenshots\observability\dashboard-order.png`: image too visually uniform (size=3840x2160, colors=223, stddev=8.0, dominant=0.3958)
- `FAIL` `D:\Projects\Services\project-validation\screenshots\observability\dashboard-platform.png`: image too visually uniform (size=3840x2160, colors=215, stddev=7.77, dominant=0.4824)
- `FAIL` `D:\Projects\Services\project-validation\screenshots\observability\dashboard-product.png`: image too visually uniform (size=3840x2160, colors=222, stddev=7.93, dominant=0.3958)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\grafana-dashboard-list.png`: image looks populated (size=3840x2160, colors=301, stddev=12.27, dominant=0.7405)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\grafana-login.png`: image looks populated (size=3840x2160, colors=2425, stddev=39.41, dominant=0.0078)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\grafana-loki-explore.png`: image looks populated (size=3840x2160, colors=489, stddev=12.64, dominant=0.2981)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\grafana-tempo-datasource.png`: image looks populated (size=3840x2160, colors=272, stddev=10.01, dominant=0.7744)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\prometheus-targets.png`: image looks populated (size=3840x2160, colors=365, stddev=40.14, dominant=0.564)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\tempo-order-trace.png`: image looks populated (size=3840x2160, colors=580, stddev=18.36, dominant=0.2429)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\tempo-product-trace.png`: image looks populated (size=3840x2160, colors=539, stddev=13.59, dominant=0.2419)
- `PASS` `D:\Projects\Services\project-validation\screenshots\observability\tempo-search.png`: image looks populated (size=3840x2160, colors=302, stddev=11.8, dominant=0.4824)
- `PASS` `D:\Projects\Services\project-validation\screenshots\secrets\vault-login.png`: image looks populated (size=3840x2160, colors=103, stddev=9.1, dominant=0.8899)
- `PASS` `D:\Projects\Services\project-validation\screenshots\secrets\vault-secret-inventory.png`: image looks populated (size=3840x2160, colors=345, stddev=77.04, dominant=0.5437)