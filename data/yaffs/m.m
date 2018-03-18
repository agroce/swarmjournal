
swarmcov=load('swarm.cov.71');
cov=load('nonswarm.cov.71');

figure;
subplot(2,1,1);
plot([1:1:size(swarmcov,1)],swarmcov(:,1),'-r','LineWidth',2);
hold on;
plot([1:1:size(cov,1)],cov(:,1),'-b','LineWidth',2);
xlabel('# 10m intervals');
ylabel('statement coverage');
legend('swarm','non-swarm');
subplot(2,1,2);
plot([1:1:size(swarmcov,1)],swarmcov(:,2),'-r','LineWidth',2);
hold on;
plot([1:1:size(cov,1)],cov(:,2),'-b','LineWidth',2);
xlabel('# 10m intervals');
ylabel('branch coverage');
legend('swarm','non-swarm');



% figure;
% subplot(2,1,1);
% hist(cov(:,2),[2000:1:2300]);
% xlabel('branch coverage');
% ylabel('# tests');
% legend('non-swarm');
% subplot(2,1,2);
% hist(swarmcov(:,2),[2000:1:2300]);
% xlabel('branch coverage');
% ylabel('# tests');
% legend('swarm');
