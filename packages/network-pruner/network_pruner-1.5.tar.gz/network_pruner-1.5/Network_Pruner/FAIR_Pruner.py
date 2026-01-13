def hello():
    print('FAIR Pruner is working well.')


#############################################################
# from scipy.stats import wasserstein_distance
import torch
import itertools
import pickle
import os
import torch.nn as nn
import random
import torch.nn.functional as F
################################################################
def wasserstein_1d(x, y):
    """
    Compute 1D Wasserstein distance (Earth Mover's Distance) between x and y.
    Supports unequal lengths and GPU tensors.
    """
    # ✅ 转成 float32（或者 float64 都行）
    x = x.flatten().to(torch.float32)
    y = y.flatten().to(torch.float32)

    x = x.sort().values.to(torch.float32)
    y = y.sort().values.to(torch.float32)

    n, m = x.size(0), y.size(0)
    if n != m:
        q = torch.linspace(0, 1, steps=max(n, m), device=x.device)
        xq = torch.quantile(x, q)
        yq = torch.quantile(y, q)
        return torch.mean(torch.abs(xq - yq))
    else:
        return torch.mean(torch.abs(x - y))



def sliced_wasserstein_distance(X, Y, n_projections=128, p=1):
    """
    Approximate Sliced Wasserstein Distance between two point clouds X, Y.
    Supports unequal sample sizes and 1D fallback.
    """
    device = X.device
    X, Y = X.to(torch.float32), Y.to(torch.float32)
    D = X.shape[1]

    # 1D 特化
    if D == 1:
        return wasserstein_1d(X, Y)

    # 生成随机方向
    theta = torch.randn((D, n_projections), device=device)
    theta = F.normalize(theta, dim=0)

    proj_X = X @ theta
    proj_Y = Y @ theta

    proj_X_sorted, _ = torch.sort(proj_X, dim=0)
    proj_Y_sorted, _ = torch.sort(proj_Y, dim=0)

    #
    proj_X_sorted = proj_X_sorted.to(torch.float32)
    proj_Y_sorted = proj_Y_sorted.to(torch.float32)
    n = max(proj_X_sorted.size(0), proj_Y_sorted.size(0))
    q = torch.linspace(0, 1, n, device=device)

    #
    proj_X_q = torch.quantile(proj_X_sorted, q, dim=0)
    proj_Y_q = torch.quantile(proj_Y_sorted, q, dim=0)

    dist = torch.mean(torch.abs(proj_X_q - proj_Y_q) ** p)
    return dist ** (1.0 / p)




def get_prunedata(prune_datasetloader,batch_size,class_num,pruning_samples_num):
    #
    # prune_datasetloader : is （from torch.utils.data import DataLoader）.
    # class_num : is the number of categories in the dataset.
    # pruning_samples_num : is the upper limit of the sample size for each category used to calculate the distance.
    #
    class_data = {}
    for type in range(class_num):
        class_data[f'{type}'] = []
    n=[0]*class_num
    for inputs, targets in prune_datasetloader:
        if sum(1 for num in n if num > pruning_samples_num)==class_num:
            break
        class_idx = {}
        for type in range(class_num):
            if n[type]<=pruning_samples_num:
                class_idx[f'{type}'] = torch.where(targets == type)[0]
                class_data[f'{type}'].append(torch.index_select(inputs, 0, class_idx[f'{type}']))
                n[type]+=len(class_idx[f'{type}'])
    for type in range(class_num):
        class_data[f'{type}'] = torch.cat(class_data[f'{type}'], dim = 0)
    prune_data = {}
    for type in range(class_num):
        bnum = class_data[f'{type}'].shape[0]//batch_size
        prune_data[f'{type}']=[]
        for i in range(bnum):
            prune_data[f'{type}'].append(class_data[f'{type}'][(i * batch_size):((i + 1) * batch_size), :])
    print('The pruning data is collated')
    return prune_data


features = {}
# 定义一个钩子函数
def get_features(name):
    def hook(model, input, output):
        if  isinstance(model, nn.GRU):
            features[name] = output[0]
        else:
            features[name] = output
    return hook


# def get_Distance(model,prunedata,layer_num,device):
#     #
#     # model: is the model we want to prune.
#     # prunedata :is the output from get_prunedata.
#     # layer_num : it the aim layer we want to compute Distance.
#     # device: torch.device('cpu') or torch.device('cuda') .
#     #
#     model.to(device)
#     # 注册钩子到每一层
#     for i,(name, layer) in enumerate(model.named_modules()):
#         if i == layer_num:
#             handle = layer.register_forward_hook(get_features(f'{i}'))
#             break
# ##############################以下是收集输出########################################
#     model.eval()
#     with torch.no_grad():
#         output_res = {}
#         for type in range(len(prunedata)):
#             output_res[f'{type}'] = []
#             for num in range(len(prunedata[f'{type}'])):
#                 model(prunedata[f'{type}'][num].to(device))
#                 if features[f'{layer_num}'].dim() == 3:
#                     output_res[f'{type}'].append(features[f'{layer_num}'])
#                 else:
#                     output_res[f'{type}'].append(features[f'{layer_num}'].view(features[f'{layer_num}'].size(0), features[f'{layer_num}'].size(1), -1).contiguous())
#     #############################以下是计算距离########################################
#
#         if features[f'{layer_num}'].dim() == 4:
#             channel_num = features[f'{layer_num}'].shape[1]
#             all_distance = [0]*channel_num
#             for combo in itertools.combinations(range(len(prunedata)), 2):
#                 for channel in range(channel_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res[f'{combo[0]}'])):
#                         xjbg0.append(output_res[f'{combo[0]}'][i][:,channel,:].contiguous())
#                     for i in range(len(output_res[f'{combo[1]}'])):
#                         xjbg1.append(output_res[f'{combo[1]}'][i][:,channel,:].contiguous())
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = ot.sliced.sliced_wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                                      xjbg1.cpu().detach().numpy(),
#                                                                      n_projections =50)
#                     if distance > all_distance[channel]:
#                         all_distance[channel] = distance
#         elif features[f'{layer_num}'].dim() == 2:
#             neuron_num = features[f'{layer_num}'].shape[1]
#             all_distance = [0] *neuron_num
#             for combo in itertools.combinations(range(len(output_res)), 2):
#                 for neuron in range(neuron_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res[f'{combo[0]}'])):
#                         xjbg0.append(output_res[f'{combo[0]}'][i][:,neuron,0].contiguous())
#                     for i in range(len(output_res[f'{combo[1]}'])):
#                         xjbg1.append(output_res[f'{combo[1]}'][i][:,neuron, 0].contiguous())
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = wasserstein_distance(xjbg0.cpu().detach().numpy(), xjbg1.cpu().detach().numpy())
#                     if distance > all_distance[neuron]:
#                         all_distance[neuron] = distance
#         elif features[f'{layer_num}'].dim() == 3:
#             hidden_num = features[f'{layer_num}'].shape[2]
#             all_distance = [0] * hidden_num
#             for combo in itertools.combinations(range(len(prunedata)), 2):
#                 for hidden in range(hidden_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res[f'{combo[0]}'])):
#                         xjbg0.append(output_res[f'{combo[0]}'][i][:, :, hidden].contiguous())
#                     for i in range(len(output_res[f'{combo[1]}'])):
#                         xjbg1.append(output_res[f'{combo[1]}'][i][:, :, hidden].contiguous())
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = ot.sliced.sliced_wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                                      xjbg1.cpu().detach().numpy(),
#                                                                      n_projections=50)
#                     if distance > all_distance[hidden]:
#                         all_distance[hidden] = distance
#
#     print(f'The Distance of the {layer_num}th layer is calculated.')
#     all_distance = torch.tensor(all_distance)
#     features.clear()
#     handle.remove()
#
#     return all_distance
#
#
# ###########################################################################################################
# ###########################################################################################################
#
# #v2：This version is the same as the previous version
# # （get_Distance）, and in order to reduce the pressure
# # on the video memory and memory, the data is saved on
# # the hard disk. Although it slows down the running
# # speed, it can be adopted in the graphics card and
# # insufficient memory space.
#
# def get_Distance2(model,prunedata,layer_num,device,path):
#     #
#     # model: is the model we want to prune
#     # prunedata :is the output from get_prunedata
#     # layer_num : it the aim layer we want to compute Distance
#     # device: torch.device('cpu') or 'cuda'
#     # path: A path to save the temporary file
#     #
#     model.to(device)
#     # 注册钩子到每一层
#     for i,(name, layer) in enumerate(model.named_modules()):
#         if i == layer_num:
#             handle = layer.register_forward_hook(get_features(f'{i}'))
#             break
# ##############################以下是收集输出########################################
#     model.eval()
#     with torch.no_grad():
#         for type in range(len(prunedata)):
#             output_res = []
#             for num in range(len(prunedata[f'{type}'])):
#                 model(prunedata[f'{type}'][num].to(device))
#                 output_res.append(features[f'{layer_num}'].view(features[f'{layer_num}'].size(0), features[f'{layer_num}'].size(1), -1).to(device))
#             with open(path+f'/layer{layer_num}_output_type{type}.pkl', 'wb') as file:
#                 pickle.dump(output_res, file)
#     #############################以下是计算距离########################################
#         if features[f'{layer_num}'].dim() == 4:
#             channel_num = features[f'{layer_num}'].shape[1]
#             all_distance = [0]*channel_num
#             for combo in itertools.combinations(range(len(prunedata)), 2):
#                 with open(path+f'/layer{layer_num}_output_type{combo[0]}.pkl', 'rb') as file:
#                     output_res0 = pickle.load(file)
#                 with open(path+f'/layer{layer_num}_output_type{combo[1]}.pkl', 'rb') as file:
#                     output_res1 = pickle.load(file)
#                 for channel in range(channel_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res0)):
#                         xjbg0.append(output_res0[i][:,channel,:])
#                     for i in range(len(output_res1)):
#                         xjbg1.append(output_res1[i][:,channel,:])
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = ot.sliced.sliced_wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                                      xjbg1.cpu().detach().numpy(),
#                                                                      n_projections =50)
#                     if distance > all_distance[channel]:
#                         all_distance[channel] = distance
#
#         elif features[f'{layer_num}'].dim() == 2:
#             neuron_num = features[f'{layer_num}'].shape[1]
#             all_distance = [0] *neuron_num
#             for combo in itertools.combinations(range(len(output_res)), 2):
#                 with open(path+f'/layer{layer_num}_output_type{combo[0]}.pkl','rb') as file:
#                     output_res0 = pickle.load(file)
#                 with open(path+f'/layer{layer_num}_output_type{combo[1]}.pkl','rb') as file:
#                     output_res1 = pickle.load(file)
#                 for neuron in range(neuron_num):
#                     # print(f'第{neuron}个神经元正在计算距离')
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res0)):
#                         xjbg0.append(output_res0[i][:,neuron,0])
#                     for i in range(len(output_res1)):
#                         xjbg1.append(output_res1[i][:,neuron,0])
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                     xjbg1.cpu().detach().numpy())
#                     if distance > all_distance[neuron]:
#                         all_distance[neuron] = distance
#         elif features[f'{layer_num}'].dim() == 3:
#             hidden_num = features[f'{layer_num}'].shape[2]
#             all_distance = [0] * hidden_num
#             for combo in itertools.combinations(range(len(prunedata)), 2):
#                 with open(path+f'/layer{layer_num}_output_type{combo[0]}.pkl','rb') as file:
#                     output_res0 = pickle.load(file)
#                 with open(path+f'/layer{layer_num}_output_type{combo[1]}.pkl','rb') as file:
#                     output_res1 = pickle.load(file)
#                 for hidden in range(hidden_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res0)):
#                         xjbg0.append(output_res0[i][:, :, hidden])
#                     for i in range(len(output_res0)):
#                         xjbg1.append(output_res0[i][:, :, hidden])
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = ot.sliced.sliced_wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                                      xjbg1.cpu().detach().numpy(),
#                                                                      n_projections=50)
#                     if distance > all_distance[hidden]:
#                         all_distance[hidden] = distance
#     print(f'The Distance of the {layer_num}th layer is calculated.')
#     all_distance = torch.tensor(all_distance)
#     features.clear()
#     handle.remove()
#     for type in range(len(prunedata)):
#         os.remove(path+f'/layer{layer_num}_output_type{type}.pkl')
#
#     return all_distance

###############################################################################################################
def build_comprehensive_index_cache(dataset, class_num=1000):
    """
    构建健壮的索引缓存，支持各种数据集类型
    """
    index_cache = {c: [] for c in range(class_num)}

    # 处理 Subset
    if isinstance(dataset, torch.utils.data.Subset):
        base_dataset = dataset.dataset
        indices = dataset.indices
    else:
        base_dataset = dataset
        indices = range(len(dataset))

    # 多种方式获取标签
    for new_idx, orig_idx in enumerate(indices):
        label = None

        # 方式1: 直接从样本获取
        if hasattr(base_dataset, 'samples'):
            _, label = base_dataset.samples[orig_idx]
        # 方式2: 从 targets 获取
        elif hasattr(base_dataset, 'targets'):
            if isinstance(base_dataset.targets, (list, tuple)):
                label = base_dataset.targets[orig_idx]
            else:  # tensor
                label = base_dataset.targets[orig_idx].item()
        # 方式3: 通过 __getitem__ 获取
        else:
            try:
                _, label = base_dataset[orig_idx]
            except (ValueError, IndexError):
                try:
                    sample = base_dataset[orig_idx]
                    if isinstance(sample, (list, tuple)) and len(sample) >= 2:
                        _, label = sample
                except:
                    continue

        if label is not None and 0 <= label < class_num:
            index_cache[label].append(new_idx)

    # 统计信息
    valid_classes = sum(1 for v in index_cache.values() if len(v) > 0)
    total_samples = sum(len(v) for v in index_cache.values())
    print(f"✅ Index cache built: {valid_classes} classes, {total_samples} samples")

    return index_cache


def sample_data_once(dataloader, index_cache, samples_per_class=50, max_classes=100):
    """
    一次性采样，返回所有选中的样本
    """
    # 选择类别
    if max_classes and len(index_cache) > max_classes:
        # class_sizes = {cls: len(indices) for cls, indices in index_cache.items()}
        # selected_classes = sorted(class_sizes, key=class_sizes.get, reverse=True)[:max_classes]
        selected_classes = random.sample(list(index_cache.keys()), max_classes)
    else:
        selected_classes = list(index_cache.keys())

    print(f"🎯 Sampling {samples_per_class} samples from {len(selected_classes)} classes...")

    # 收集样本
    class_samples = {}
    for cls in selected_classes:
        if cls in index_cache and len(index_cache[cls]) >= samples_per_class:
            selected_indices = random.sample(index_cache[cls], samples_per_class)
            samples = [dataloader.dataset[idx][0] for idx in selected_indices]
            class_samples[cls] = torch.stack(samples)
        else:
            print(f"⚠️ Class {cls} has insufficient samples: {len(index_cache.get(cls, []))}")

    print(f"✅ Sampling completed: {sum(len(s) for s in class_samples.values())} total samples")
    return class_samples


def get_layer_distance_memory_efficient(model, layer_num, class_samples, device):
    """
    内存高效版本：动态提取特征，不保存所有特征
    """
    model.to(device)

    # 注册当前层的钩子
    for i, (name, layer) in enumerate(model.named_modules()):
        if i == layer_num:
            handle = layer.register_forward_hook(get_features(f'{layer_num}'))
            break

    model.eval()

    # 获取特征维度信息（用第一个类别测试）
    first_cls = list(class_samples.keys())[0]
    test_sample = class_samples[first_cls][:1].to(device)
    with torch.no_grad():
        model(test_sample)
        feat = features.get(f'{layer_num}')
        if feat is None:
            print(f"⚠️ No features found for layer {layer_num}")
            handle.remove()
            return None

        # 确定特征维度
        if feat.dim() == 4:  # CNN特征 [batch, channels, H, W]
            channel_num = feat.shape[1]
            all_distance = [0] * channel_num
            feat_type = 'cnn'
        elif feat.dim() == 2:  # 全连接特征 [batch, features]
            neuron_num = feat.shape[1]
            all_distance = [0] * neuron_num
            feat_type = 'fc'
        elif feat.dim() == 3:  # RNN特征 [batch, seq_len, hidden]
            hidden_num = feat.shape[2]
            all_distance = [0] * hidden_num
            feat_type = 'rnn'
        else:
            print(f"⚠️ Unsupported feature dimension {feat.dim()}")
            handle.remove()
            return None

    print(f"  Processing {len(all_distance)} units ({feat_type} features)")

    # 获取类别列表并排序
    class_list = sorted(class_samples.keys())
    total_pairs = len(class_list) * (len(class_list) - 1) // 2

    print(f"  Computing {total_pairs} class pairs...")

    # 外层循环：k1 从 1 到 K-1（实际索引从第二个开始）
    for i in range(1, len(class_list)):
        k1 = class_list[i]

        # 🎯 提取 k1 的特征（只提取一次，用于所有与 k2 的配对）
        features_k1 = extract_class_features(
            model, class_samples[k1], device, layer_num, feat_type)

        if features_k1 is None:
            continue

        # 内层循环：k2 从 0 到 i-1
        for j in range(i):
            k2 = class_list[j]

            # 🎯 提取 k2 的特征
            features_k2 = extract_class_features(
                model, class_samples[k2], device, layer_num, feat_type)

            if features_k2 is None:
                continue

            # 🎯 计算距离并更新最大值
            update_distances(all_distance, features_k1, features_k2,
                             feat_type, device)

            # 🎯 立即丢弃 k2 的特征
            del features_k2
            torch.cuda.empty_cache()

        # 🎯 处理完所有 k2 后，丢弃 k1 的特征
        del features_k1
        torch.cuda.empty_cache()

        # 进度显示
        if i % 200 == 0:
            completed_pairs = i * (i + 1) // 2
            print(f"    Progress: {completed_pairs}/{total_pairs} pairs "
                  f"({completed_pairs / total_pairs * 100:.1f}%)")

    # 清理
    features.clear()
    handle.remove()

    print(f"✅ Layer {layer_num} completed")
    return torch.tensor(all_distance)


def get_layer_distance(model, layer_num, class_samples, device,
                                   sample_classes=10, num_iterations=500):
    """
    蒙特卡洛版本：重复采样类别对，记录最大距离
    """
    model.to(device)

    # 注册当前层的钩子
    for i, (name, layer) in enumerate(model.named_modules()):
        if i == layer_num:
            handle = layer.register_forward_hook(get_features(f'{layer_num}'))
            break

    model.eval()

    # 获取特征维度信息
    first_cls = list(class_samples.keys())[0]
    test_sample = class_samples[first_cls][:1].to(device)
    with torch.no_grad():
        model(test_sample)
        feat = features.get(f'{layer_num}')
        if feat is None:
            print(f"⚠️ No features found for layer {layer_num}")
            handle.remove()
            return None

        # 确定特征维度
        if feat.dim() == 4:  # CNN特征
            channel_num = feat.shape[1]
            all_distance = [0] * channel_num
            feat_type = 'cnn'
        elif feat.dim() == 2:  # 全连接特征
            neuron_num = feat.shape[1]
            all_distance = [0] * neuron_num
            feat_type = 'fc'
        elif feat.dim() == 3:  # RNN特征
            hidden_num = feat.shape[2]
            all_distance = [0] * hidden_num
            feat_type = 'rnn'
        else:
            print(f"⚠️ Unsupported feature dimension {feat.dim()}")
            handle.remove()
            return None

    # print(
    #     f"  Processing {len(all_distance)} units, {sample_classes} classes per iteration, {num_iterations} iterations")

    # 所有可用类别
    all_classes = list(class_samples.keys())


    for iteration in range(num_iterations):
        # if iteration % 200 == 0:
        #     print(f"    Iteration {iteration + 1}/{num_iterations}")

        # 1. 随机采样类别
        sampled_classes = random.sample(all_classes, sample_classes)

        # 2. 计算这些类别中所有配对的距离
        for k1, k2 in itertools.combinations(sampled_classes, 2):
            # 提取特征
            features_k1 = extract_class_features(
                model, class_samples[k1], device, layer_num, feat_type)
            features_k2 = extract_class_features(
                model, class_samples[k2], device, layer_num, feat_type)

            if features_k1 is None or features_k2 is None:
                continue

            # 计算距离并更新最大值
            update_distances_max(all_distance, features_k1, features_k2, feat_type, device)

            # 清理
            del features_k1, features_k2
            torch.cuda.empty_cache()

    # 清理
    features.clear()
    handle.remove()

    print(f"✅ The Distance of layer {layer_num} is calculated.")
    return torch.tensor(all_distance)


def update_distances_max(all_distance, features1, features2, feat_type, device):
    """
    计算距离并只更新最大值（不累加）
    """
    features1_gpu = [f.to(device) for f in features1]
    features2_gpu = [f.to(device) for f in features2]

    if feat_type == 'cnn':
        channel_num = features1_gpu[0].shape[1]
        for channel in range(channel_num):
            x0 = torch.cat([f[:, channel, :] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, channel, :] for f in features2_gpu], dim=0)
            distance = sliced_wasserstein_distance(x0, x1, n_projections=128)
            if distance > all_distance[channel]:
                all_distance[channel] = distance

    elif feat_type == 'fc':
        neuron_num = features1_gpu[0].shape[1]
        for neuron in range(neuron_num):
            x0 = torch.cat([f[:, neuron, 0] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, neuron, 0] for f in features2_gpu], dim=0)
            distance = wasserstein_1d(x0, x1)
            if distance > all_distance[neuron]:
                all_distance[neuron] = distance

    elif feat_type == 'rnn':
        hidden_num = features1_gpu[0].shape[2]
        for hidden in range(hidden_num):
            x0 = torch.cat([f[:, :, hidden] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, :, hidden] for f in features2_gpu], dim=0)
            distance = sliced_wasserstein_distance(x0, x1, n_projections=64)
            if distance > all_distance[hidden]:
                all_distance[hidden] = distance

    # 清理GPU内存
    del features1_gpu, features2_gpu
    torch.cuda.empty_cache()


def extract_class_features(model, samples, device, layer_num, feat_type):
    """
    提取单个类别的特征
    """
    features_list = []
    batch_size = min(256, len(samples))
    with torch.no_grad():
        for i in range(0, len(samples), batch_size):
            batch = samples[i:i + batch_size].to(device)
            model(batch)

            feat = features.get(f'{layer_num}')
            if feat is not None:
                # 根据特征类型处理
                if feat_type == 'cnn':
                    # CNN: [batch, channels, H, W] -> [batch, channels, H*W]
                    feat_processed = feat.view(feat.size(0), feat.size(1), -1)
                elif feat_type == 'fc':
                    # FC: [batch, features] -> [batch, features, 1]
                    feat_processed = feat.unsqueeze(-1)
                elif feat_type == 'rnn':
                    # RNN: [batch, seq_len, hidden] 保持原样
                    feat_processed = feat
                else:
                    feat_processed = feat

                features_list.append(feat_processed)  # 移到CPU保存.cpu()

            del batch
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    return features_list if features_list else None


def update_distances(all_distance, features1, features2, feat_type, device):
    """
    计算两个类别特征的距离并更新最大值
    """
    # 移动到GPU计算
    features1_gpu = [f.to(device) for f in features1]
    features2_gpu = [f.to(device) for f in features2]

    if feat_type == 'cnn':
        # CNN: 对每个通道计算距离
        channel_num = features1_gpu[0].shape[1]
        for channel in range(channel_num):
            x0 = torch.cat([f[:, channel, :] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, channel, :] for f in features2_gpu], dim=0)
            distance = sliced_wasserstein_distance(x0, x1, n_projections=128)
            if distance > all_distance[channel]:
                all_distance[channel] = distance

    elif feat_type == 'fc':
        # FC: 对每个神经元计算距离
        neuron_num = features1_gpu[0].shape[1]
        for neuron in range(neuron_num):
            x0 = torch.cat([f[:, neuron, 0] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, neuron, 0] for f in features2_gpu], dim=0)
            distance = wasserstein_1d(x0, x1)
            if distance > all_distance[neuron]:
                all_distance[neuron] = distance

    elif feat_type == 'rnn':
        # RNN: 对每个隐藏单元计算距离
        hidden_num = features1_gpu[0].shape[2]
        for hidden in range(hidden_num):
            x0 = torch.cat([f[:, :, hidden] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, :, hidden] for f in features2_gpu], dim=0)
            distance = sliced_wasserstein_distance(x0, x1, n_projections=128)
            if distance > all_distance[hidden]:
                all_distance[hidden] = distance

    # 清理GPU内存
    del features1_gpu, features2_gpu
    torch.cuda.empty_cache()


###################################################################################################################
# 创建一个字典来存储每一层的梯度
gradients = {}
# 定义一个钩子函数来获取梯度
def get_grad(name):
    def hook(module, grad_input, grad_output):
        # grad_input是输入的梯度，grad_output是输出的梯度
        gradients[name] = grad_output[0]
    return hook

# 定义一个钩子函数来捕获GRU model权重的梯度
gru1_weight_ih_grad = None
gru1_weight_hh_grad = None

def hook_gru1_weight_ih(grad):
    global gru1_weight_ih_grad
    gru1_weight_ih_grad = grad

def hook_gru1_weight_hh(grad):
    global gru1_weight_hh_grad
    gru1_weight_hh_grad = grad

# def get_ReconstructionError(model,prune_datasetloader,layer_num,device,loss_function):
#     #
#     # model: is the model we want to prune.
#     # prune_datasetloader : is （from torch.utils.data import DataLoader）.
#     # layer_num : it the aim layer we want to compute Distance.
#     # device: torch.device('cpu') or torch.device('cuda') .
#     # loss_function: The loss function used for model training.
#     #
#
#     model.to(device)
#     model.train()
#     if isinstance(list(model.named_modules())[layer_num][1],nn.GRU):
#         the_wih = list(model.named_modules())[layer_num][1].weight_ih_l0.data
#         the_whh = list(model.named_modules())[layer_num][1].weight_hh_l0.data
#         the_Bias_ih = list(model.named_modules())[layer_num][1].bias_ih_l0.data
#         the_Bias_hh = list(model.named_modules())[layer_num][1].bias_hh_l0.data
#         loss_fun = loss_function
#         loss_fun.to(device)
#         gradient = torch.zeros(the_wih.shape[0]).to(device)  # shape[0]
#         hinden_num = the_wih.shape[0]
#         for inputs, targets in prune_datasetloader:
#             inputs = inputs.to(device)
#             targets = targets.to(device)
#             output = model(inputs)
#             loss = loss_fun(output, targets)
#             loss.backward()
#             gradient += torch.sum(list(model.named_modules())[layer_num][1].weight_ih_l0.grad * the_wih,dim=1)
#             gradient += torch.sum(list(model.named_modules())[layer_num][1].weight_hh_l0.grad * the_whh,dim=1)
#             gradient += list(model.named_modules())[layer_num][1].bias_ih_l0.grad * the_Bias_ih
#             gradient += list(model.named_modules())[layer_num][1].bias_hh_l0.grad * the_Bias_hh
#         gradient = gradient[0:int(hinden_num/3)] + gradient[int(hinden_num/3):int(hinden_num/3*2)] + gradient[int(hinden_num/3*2):]
#     else:
#         the_weight = list(model.named_modules())[layer_num][1].weight.data
#         dim = the_weight.dim()
#         the_bias = list(model.named_modules())[layer_num][1].bias.data.view(the_weight.shape[0], *([1] * (dim - 1)))
#         # print(the_weight.shape)
#         loss_fun = loss_function
#         loss_fun.to(device)
#         gradient = torch.zeros(the_weight.shape).to(device)#shape[0]
#         # print(gradients[f'{layer_num}'].shape)
#         for inputs, targets in prune_datasetloader:
#             inputs = inputs.to(device)
#             targets = targets.to(device)
#             output = model(inputs)
#             loss = loss_fun(output, targets)
#             loss.backward()
#             gradient += list(model.named_modules())[layer_num][1].weight.grad * the_weight
#             gradient += list(model.named_modules())[layer_num][1].bias.grad.view(the_weight.shape[0], *([1] * (dim - 1))) * the_bias
#         gradient = torch.sum(gradient,dim = list(range(1,gradient.dim())))
#     print(f'The Reconstruction Error of the {layer_num}th layer is calculated.')
#     gradients.clear()
#
#     return gradient
# ################################################
# ################################################
# # The only difference between the two versions is
# # whether the gradient is zeroed out on each
# # calculation, and empirically the first version
# #（get_ReconstructionError）works better
# def get_ReconstructionError2(model,prune_datasetloader,layer_num,device,loss_function):
#     #
#     # model: is the model we want to prune.
#     # prune_datasetloader : is （from torch.utils.data import DataLoader）.
#     # layer_num : it the aim layer we want to compute Distance.
#     # device: torch.device('cpu') or torch.device('cuda') .
#     # loss_function: The loss function used for model training.
#     #
#     model.to(device)
#     model.train()
#     if isinstance(list(model.named_modules())[layer_num][1],nn.GRU):
#         the_wih = list(model.named_modules())[layer_num][1].weight_ih_l0.data
#         the_whh = list(model.named_modules())[layer_num][1].weight_hh_l0.data
#         the_Bias_ih = list(model.named_modules())[layer_num][1].bias_ih_l0.data
#         the_Bias_hh = list(model.named_modules())[layer_num][1].bias_hh_l0.data
#         loss_fun = loss_function
#         loss_fun.to(device)
#         gradient = torch.zeros(the_wih.shape[0]).to(device)  # shape[0]
#         hinden_num = the_wih.shape[0]
#         for inputs, targets in prune_datasetloader:
#             inputs = inputs.to(device)
#             targets = targets.to(device)
#             output = model(inputs)
#             loss = loss_fun(output, targets)
#             loss.backward()
#             gradient += torch.sum(list(model.named_modules())[layer_num][1].weight_ih_l0.grad * the_wih,dim=1)
#             gradient += torch.sum(list(model.named_modules())[layer_num][1].weight_hh_l0.grad * the_whh,dim=1)
#             gradient += list(model.named_modules())[layer_num][1].bias_ih_l0.grad * the_Bias_ih
#             gradient += list(model.named_modules())[layer_num][1].bias_hh_l0.grad * the_Bias_hh
#         gradient = gradient[0:int(hinden_num/3)] + gradient[int(hinden_num/3):int(hinden_num/3*2)] + gradient[int(hinden_num/3*2):]
#     else:
#         the_weight = list(model.named_modules())[layer_num][1].weight.data
#         dim = the_weight.dim()
#         the_bias = list(model.named_modules())[layer_num][1].bias.data.view(the_weight.shape[0], *([1] * (dim- 1)))
#         loss_fun = nn.CrossEntropyLoss()
#         loss_fun.to(device)
#         model.zero_grad()
#         for inputs, targets in prune_datasetloader:
#             inputs = inputs.to(device)
#             targets = targets.to(device)
#             output = model(inputs)
#             loss = loss_fun(output, targets)
#             loss.backward()
#         gradient = (list(model.named_modules())[layer_num][1].weight.grad * the_weight +
#                     list(model.named_modules())[layer_num][1].bias.grad.view(the_weight.shape[0],*([1] * (dim - 1))) * the_bias)
#         gradient = torch.sum(gradient,dim = list(range(1,gradient.dim())))
#     print(f'The Reconstruction Error of the {layer_num}th layer is calculated.')
#     gradients.clear()
#
#     return gradient
###################################################################################################################################

def get_ReconstructionScore_fast(model, prune_loader, layer_num, device, loss_function):
    model.to(device)
    model.train()

    target_layer = list(model.named_modules())[layer_num][1]

    # 冻结其他层，只保留目标层梯度
    for name, param in model.named_parameters():
        param.requires_grad_(False)
    for param in target_layer.parameters():
        param.requires_grad_(True)

    grad_accum = None  # 🚨 不要用 Python 整数当初始值
    use_amp = (device.type == 'cuda')
    for inputs, targets in prune_loader:
        inputs = inputs.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        model.zero_grad(set_to_none=True)

        try: # PyTorch (>= 1.14)
            scaler = torch.amp.GradScaler(enabled=use_amp)
            output = model(inputs)
            loss = loss_function(output, targets)
            scaler.scale(loss).backward()
        except AttributeError:
            try: # PyTorch (>= 1.6)
                from torch.cuda.amp import GradScaler
                scaler = GradScaler(enabled=use_amp)
                output = model(inputs)
                loss = loss_function(output, targets)
                scaler.scale(loss).backward()
            except ImportError: # older,close AMP
                use_amp = False
                output = model(inputs)
                loss = loss_function(output, targets)
                loss.backward()

        grad_w = target_layer.weight.grad  # 不需要 grad
        contrib_w = (grad_w * target_layer.weight).sum(dim=list(range(1, grad_w.dim())))

        if target_layer.bias is not None:
            grad_b = target_layer.bias.grad
            contrib_b = grad_b * target_layer.bias

        # 2. ✅ 在 no_grad 里做累计 / 或者用 detach()
        with torch.no_grad():
            if target_layer.bias is not None:
                contrib = contrib_w + contrib_b
                if grad_accum is None:
                    grad_accum = contrib.clone()
                else:
                    grad_accum.add_(contrib)
            else:
                contrib = contrib_w
                if grad_accum is None:
                    grad_accum = contrib.clone()
                else:
                    grad_accum.add_(contrib)

        # 3. 及时释放中间变量
        del output, loss, contrib_w, contrib_b, contrib
        if device.type == 'cuda':
            torch.cuda.empty_cache()

    print(f"✅ The Reconstruction Score of layer {layer_num} is calculated.")

    # 4. 恢复 requires_grad
    for param in model.parameters():
        param.requires_grad_(True)

    # 5. 返回 CPU 上的绝对值
    return grad_accum.abs().detach().cpu()

########################################################################################################################

def get_k_list(results,the_list_of_layers_to_prune,ToD_level=0.005):
    #
    # results: resluts save from main
    # the_list_of_layers_to_compute_Distance: a list of the layer number which we want to get Distance
    # the_list_of_layers_to_prune: a list of the layer number which we want to get ReconstructionError
    # FDR_level

    # results[f'D_{len(the_list_of_layers_to_prune) - 1}_s2b_idx'] = list(range(1000))
    k_list = []
    for j in range((len(the_list_of_layers_to_prune))):
        # if (j + 1) == len(the_list_of_layers_to_prune):
        #     k_list.append(0)
        #     break
        neuron_number = len(results[f'D_{j}_s2b_idx'])
        # m = int((1-2*FDR_level)*neuron_number)
        for i in range(int(0.99 * neuron_number)):
            k = int(0.99 * neuron_number) - i
            intersection = list(
                set(results[f'D_{j}_s2b_idx'][:k]) & set(results[f'RE_{j}_hat_s2b_idx'][int(neuron_number - k):]))
            # print(len(intersection)/k)
            if len(intersection) / k <= ToD_level:
                print(f'The prunable set size for layer {the_list_of_layers_to_prune[j]}th is {k}')
                k_list.append(k)
                break
            # if i == (int(0.99 * neuron_number) - 1):
            #     print(f'The {the_list_of_layers_to_prune[j]}th layer is inspected and does not need to be pruned')
            #     k_list.append(0)
            #     break
    return k_list


#######################################################################################################################

def FAIR_Pruner_get_results(model,prune_datasetloader,results_save_path,the_list_of_layers_to_prune,the_list_of_layers_to_compute_Distance,loss_function,device,class_num,the_samplesize_for_compute_distance=16,class_num_for_distance=None,num_iterations=1):
    # with open(data_path, 'rb') as f:
    #     prune_datasetloader = pickle.load(f)
    # model = torch.load(model_path)
    index_cache = build_comprehensive_index_cache(prune_datasetloader.dataset, class_num=class_num)
    if class_num_for_distance is None:
        class_num_for_distance = class_num
    class_samples = sample_data_once(prune_datasetloader, index_cache, the_samplesize_for_compute_distance, class_num)
    results = {}
    for layer_num in range(len(the_list_of_layers_to_prune)):
        results[f'RE_{layer_num}_hat'] = get_ReconstructionScore_fast(model, prune_datasetloader,
                                                                layer_num=the_list_of_layers_to_prune[layer_num],
                                                                device=device, loss_function=loss_function)
        results[f'RE_{layer_num}_hat_s2b_idx'] = torch.argsort(results[f'RE_{layer_num}_hat']).tolist()
        torch.cuda.empty_cache()
        results[f'D_{layer_num}'] = get_layer_distance(model,layer_num=the_list_of_layers_to_compute_Distance[layer_num],class_samples=class_samples, device=device, sample_classes=class_num_for_distance, num_iterations=num_iterations)
        results[f'D_{layer_num}_s2b_idx'] = torch.argsort(results[f'D_{layer_num}']).tolist()
        torch.cuda.empty_cache()
    with open(results_save_path, 'wb') as file:
        pickle.dump(results, file)
    return results

import copy
from typing import Optional

import torch
import torch.nn as nn
from torch.optim import SGD
from torch.utils.data import DataLoader


@torch.no_grad()
def _evaluate(model: nn.Module, val_loader: DataLoader, criterion: nn.Module, device: torch.device) -> float:
    """Return average validation loss."""
    model.eval()
    total_loss, total_n = 0.0, 0

    for batch in val_loader:
        # 默认 batch=(inputs, targets). 如果你的 batch 是 dict，在这里改取值方式
        inputs, targets = batch
        inputs = inputs.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        logits = model(inputs)  # [B, C]
        loss = criterion(logits, targets)

        bs = targets.size(0)
        total_loss += loss.item() * bs
        total_n += bs

    return total_loss / max(total_n, 1)


def finetune_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int,
    *,
    lr: float = 1e-2,
    momentum: float = 0.9,
    weight_decay: float = 0.0,
    nesterov: bool = False,
    device: Optional[str] = None,
    grad_clip_norm: Optional[float] = None,
    amp: bool = True,
    log_every: int = 50,
) -> nn.Module:
    """
    微调函数（多分类）：
    - Loss: CrossEntropyLoss
    - Optim: SGD
    - 返回：验证集上 val_loss 最佳的模型（权重已加载，不保存本地）
    """
    dev = torch.device(device) if device is not None else torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    model = model.to(dev)

    criterion = nn.CrossEntropyLoss()
    optimizer = SGD(
        model.parameters(),
        lr=lr,
        momentum=momentum,
        weight_decay=weight_decay,
        nesterov=nesterov,
    )

    use_amp = bool(amp and dev.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    best_state = copy.deepcopy(model.state_dict())
    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        model.train()
        run_loss, run_correct, run_n = 0.0, 0, 0

        for step, batch in enumerate(train_loader, start=1):
            inputs, targets = batch
            inputs = inputs.to(dev, non_blocking=True)
            targets = targets.to(dev, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            with torch.cuda.amp.autocast(enabled=use_amp):
                logits = model(inputs)          # [B, C]
                loss = criterion(logits, targets)

            scaler.scale(loss).backward()

            if grad_clip_norm is not None:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)

            scaler.step(optimizer)
            scaler.update()

            bs = targets.size(0)
            run_loss += loss.item() * bs
            run_correct += (logits.detach().argmax(dim=1) == targets).sum().item()
            run_n += bs

            if log_every > 0 and (step % log_every == 0):
                print(
                    f"[Epoch {epoch}/{epochs}] step {step}/{len(train_loader)} | "
                    f"train_loss={run_loss/max(run_n,1):.4f} train_acc={run_correct/max(run_n,1):.4f}"
                )

        # validate & track best
        val_loss = _evaluate(model, val_loader, criterion, dev)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = copy.deepcopy(model.state_dict())

        print(
            f"[Epoch {epoch}/{epochs}] "
            f"train_loss={run_loss/max(run_n,1):.4f} train_acc={run_correct/max(run_n,1):.4f} | "
            f"val_loss={val_loss:.4f} (best={best_val_loss:.4f})"
        )

    # load best weights (no local saving)
    model.load_state_dict(best_state)
    return model


import copy
import operator
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Union, Any
from collections import deque

import torch
import torch.nn as nn
import torch.fx as fx
from torch.fx.passes.shape_prop import ShapeProp


# =========================
# Utils: shapes & indices
# =========================

@dataclass
class Spec:
    shape: Tuple[int, ...]
    c_axis: Optional[int]  # NCHW->1, (N,F)->1, (N,T,C)->-1


def _get_shape(node: fx.Node) -> Optional[Tuple[int, ...]]:
    tm = node.meta.get("tensor_meta", None)
    if tm is None:
        return None
    shp = getattr(tm, "shape", None)
    if shp is None:
        return None
    return tuple(int(x) for x in shp)


def _default_c_axis(shape: Tuple[int, ...]) -> Optional[int]:
    if len(shape) == 4:
        return 1
    if len(shape) == 2:
        return 1
    if len(shape) == 3:
        return -1
    return None


def _to_long_idx(x: Union[List[int], torch.Tensor], device="cpu") -> torch.Tensor:
    if isinstance(x, torch.Tensor):
        return x.to(device=device, dtype=torch.long)
    return torch.tensor(list(x), dtype=torch.long, device=device)


def _full_idx(n: int, device="cpu") -> torch.Tensor:
    return torch.arange(int(n), dtype=torch.long, device=device)


def _expand_channel_idx_to_flat_features(ch_idx: torch.Tensor, spatial: int) -> torch.Tensor:
    # [c0,c1,...] -> [c0*sp:(c0+1)*sp, c1*sp:(c1+1)*sp, ...]
    if spatial <= 1:
        return ch_idx
    out = []
    for c in ch_idx.tolist():
        out.append(torch.arange(c * spatial, (c + 1) * spatial, dtype=torch.long, device=ch_idx.device))
    return torch.cat(out, dim=0) if out else ch_idx.new_empty((0,), dtype=torch.long)


def _is_depthwise_conv(m: nn.Module) -> bool:
    return isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d)) and (m.groups == m.in_channels == m.out_channels)


# =========================
# Trace: find nearest Conv/Linear as "channel source"
# =========================

def _trace_channel_source(node: fx.Node, gm: fx.GraphModule) -> Optional[str]:
    """BFS trace backward to find nearest Conv/Linear module target name."""
    modules = dict(gm.named_modules())
    q = deque([node])
    visited = set()

    def push(v):
        if isinstance(v, fx.Node):
            q.append(v)
        elif isinstance(v, (list, tuple)):
            for vv in v:
                push(vv)

    while q:
        cur = q.popleft()
        if not isinstance(cur, fx.Node) or cur in visited:
            continue
        visited.add(cur)

        if cur.op == "call_module":
            m = modules.get(cur.target, None)
            if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                              nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d,
                              nn.Linear)):
                return cur.target
            # passthrough first input
            if cur.args:
                push(cur.args[0])
            continue

        if cur.op == "call_function":
            for a in cur.args:
                push(a)
            for a in cur.kwargs.values():
                push(a)
            continue

        if cur.op == "call_method":
            if cur.args:
                push(cur.args[0])
            continue

    return None


# =========================
# Build keep_out_idx_map from your results + named_modules indices
# =========================

def build_keep_out_idx_map_from_results(
    original_model: nn.Module,
    the_list_of_layers_to_prune: List[int],  # indices in list(original_model.named_modules())
    k_list: List[int],
    results: Dict[str, Any],
    key_fmt: str = "D_{j}_s2b_idx",
    device: str = "cpu",
) -> Dict[str, torch.Tensor]:
    """
    results[key_fmt.format(j=j)] should be a list of channel indices sorted small->big by importance.
    We prune first k, keep the rest.
    Returns: {module_path: keep_out_idx_tensor(sorted)}
    """
    named = list(original_model.named_modules())
    assert len(the_list_of_layers_to_prune) == len(k_list), "prune list and k_list length mismatch"

    keep_out: Dict[str, torch.Tensor] = {}
    for j, (idx, k) in enumerate(zip(the_list_of_layers_to_prune, k_list)):
        path, m = named[idx]
        key = key_fmt.format(j=j)
        if key not in results:
            raise KeyError(f"results missing key: {key}")

        pos = results[key]
        pos = _to_long_idx(pos, device=device)

        k = int(k)
        if k < 0:
            k = 0
        if k >= pos.numel():
            # keep at least 1
            keep = pos[:1]
        else:
            keep = pos[k:]

        keep = torch.sort(keep).values

        # sanity with out dim
        out0 = None
        if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                          nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)):
            out0 = int(m.out_channels)
        elif isinstance(m, nn.Linear):
            out0 = int(m.out_features)
        else:
            raise RuntimeError(f"Not Conv/Linear at idx={idx}: {path} -> {type(m).__name__}")

        keep = keep[(keep >= 0) & (keep < out0)]
        if keep.numel() == 0:
            keep = _full_idx(out0, device=device)[:1]

        keep_out[path] = keep

    return keep_out


# =========================
# Align keep_out indices for residual add (make both sides use SAME indices)
# =========================

class _UF:
    def __init__(self):
        self.p = {}
    def find(self, x):
        if x not in self.p:
            self.p[x] = x
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra
    def groups(self):
        g = {}
        for x in list(self.p.keys()):
            r = self.find(x)
            g.setdefault(r, []).append(x)
        return list(g.values())


def _outdim_of(m: nn.Module) -> int:
    if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                      nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)):
        return int(m.out_channels)
    if isinstance(m, nn.Linear):
        return int(m.out_features)
    raise TypeError(type(m).__name__)


def align_keep_out_idx_for_add(
    model: nn.Module,
    keep_out_idx: Dict[str, torch.Tensor],
    pruned_model: nn.Module,
    example_inputs: Tuple[torch.Tensor, ...],
    verbose: bool = True,
) -> Dict[str, torch.Tensor]:
    """
    For every residual add where both branches have same original shape,
    force the traced source Conv/Linear modules to use the same keep_out_idx.
    Rule: choose a deterministic canonical index set with length = pruned out_dim (少剪不多剪 in structure already fixed dim).
    """
    gm = fx.symbolic_trace(model)
    ShapeProp(gm).propagate(*example_inputs)
    mods = dict(gm.named_modules())
    uf = _UF()

    _aten_add = None
    try:
        _aten_add = torch.ops.aten.add.Tensor
    except Exception:
        _aten_add = None

    def is_add_node(n: fx.Node) -> bool:
        if n.op == "call_function" and n.target in {operator.add, torch.add}:
            return True
        if _aten_add is not None and n.op == "call_function" and n.target is _aten_add:
            return True
        if n.op == "call_method" and n.target in ("add", "__add__", "__iadd__"):
            return True
        return False

    def get_add_args(n: fx.Node):
        if n.op == "call_method":
            return n.args[0], n.args[1]
        return n.args[0], n.args[1]

    # union sources
    for node in gm.graph.nodes:
        if not is_add_node(node) or len(node.args) < 2:
            continue
        a, b = get_add_args(node)
        if not isinstance(a, fx.Node) or not isinstance(b, fx.Node):
            continue
        sa, sb, so = _get_shape(a), _get_shape(b), _get_shape(node)
        if sa is None or sb is None or so is None:
            continue
        if sa != sb or sa != so:
            continue

        src_a = _trace_channel_source(a, gm)
        src_b = _trace_channel_source(b, gm)
        if src_a is None or src_b is None:
            continue

        ma, mb = mods.get(src_a), mods.get(src_b)
        if ma is None or mb is None:
            continue
        if _outdim_of(ma) != _outdim_of(mb):
            continue

        uf.union(src_a, src_b)

    # adjust keep idx inside each group
    aligned = dict(keep_out_idx)
    pruned_mods = dict(pruned_model.named_modules())

    for group in uf.groups():
        # pruned out_dim should be same for all modules in group (after structure alignment)
        # pick from first that exists in pruned_model
        keep_len = None
        for nm in group:
            if nm in pruned_mods and isinstance(pruned_mods[nm], (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                                                                 nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d,
                                                                 nn.Linear)):
                keep_len = _outdim_of(pruned_mods[nm])
                break
        if keep_len is None:
            continue

        # collect candidate sets in original indexing
        candidates = []
        out0 = _outdim_of(mods[group[0]])
        for nm in group:
            if nm in aligned:
                candidates.append(aligned[nm].detach().cpu())
            else:
                candidates.append(_full_idx(out0).cpu())

        # canonical: try intersection; if too small, use sorted union then take first keep_len
        inter = candidates[0]
        for t in candidates[1:]:
            inter = torch.tensor(sorted(set(inter.tolist()).intersection(set(t.tolist()))), dtype=torch.long)
        if inter.numel() >= keep_len:
            canon = inter[:keep_len]
        else:
            uni = sorted(set().union(*[set(t.tolist()) for t in candidates]))
            canon = torch.tensor(uni[:keep_len], dtype=torch.long)

        # write back for members that are actually pruned or used
        changed = False
        for nm in group:
            if nm in aligned:
                if aligned[nm].numel() != keep_len or not torch.equal(aligned[nm].cpu(), canon):
                    aligned[nm] = canon.to(device=aligned[nm].device, dtype=torch.long)
                    changed = True
            else:
                # if not explicitly pruned, still ok not to store
                pass

        if verbose and changed:
            print(f"[add-align-idx] {group}: force keep_idx len={keep_len}")

    return aligned


# =========================
# Main: copy params using FX-propagated in_idx/out_idx
# =========================

@torch.no_grad()
def copy_params_to_pruned_model_fx(
    original_model: nn.Module,
    pruned_model: nn.Module,
    keep_out_idx: Dict[str, torch.Tensor],
    example_inputs: Union[torch.Tensor, Tuple[torch.Tensor, ...]],
    align_add: bool = True,
    verbose: bool = True,
    strict: bool = True,
) -> nn.Module:
    """
    Copy Conv/Linear/BN/GN parameters from original_model to pruned_model.
    - keep_out_idx: {module_path: kept output indices in ORIGINAL indexing}
    - in_idx is inferred by propagating indices on FX graph of original_model.
    Limitations (reasonable for "general CNNs"):
      - supports common ops: add, cat(dim=channel), relu-like, pool, flatten, view(N,-1).
      - if you have exotic channel-mangling ops, strict=True will raise.
    """
    device = next(pruned_model.parameters()).device if any(True for _ in pruned_model.parameters()) else torch.device("cpu")
    original_model = original_model.to(device).eval()
    pruned_model = pruned_model.to(device).eval()

    if isinstance(example_inputs, torch.Tensor):
        example_inputs = (example_inputs,)
    example_inputs = tuple(t.to(device) for t in example_inputs)

    # optional: align indices for residual add
    if align_add:
        keep_out_idx = align_keep_out_idx_for_add(original_model, keep_out_idx, pruned_model, example_inputs, verbose=verbose)

    # trace original
    gm = fx.symbolic_trace(original_model)
    ShapeProp(gm).propagate(*example_inputs)
    mods = dict(gm.named_modules())

    # spec + keep_idx on channel/feature axis (in ORIGINAL indexing)
    spec: Dict[fx.Node, Spec] = {}
    kidx: Dict[fx.Node, Optional[torch.Tensor]] = {}  # keep indices along channel/feature axis

    placeholders = [n for n in gm.graph.nodes if n.op == "placeholder"]
    if len(placeholders) != len(example_inputs):
        raise RuntimeError("example_inputs 数量与 forward 输入不一致")

    for n, t in zip(placeholders, example_inputs):
        shp = tuple(int(x) for x in t.shape)
        spec[n] = Spec(shape=shp, c_axis=_default_c_axis(shp))
        if spec[n].c_axis is None:
            kidx[n] = None
        else:
            cax = spec[n].c_axis
            if cax < 0:
                cax = len(shp) + cax
            kidx[n] = _full_idx(shp[cax], device=device)

    def _sp(x) -> Optional[Spec]:
        return spec.get(x, None) if isinstance(x, fx.Node) else None

    def _ki(x) -> Optional[torch.Tensor]:
        return kidx.get(x, None) if isinstance(x, fx.Node) else None

    _aten_add = None
    try:
        _aten_add = torch.ops.aten.add.Tensor
    except Exception:
        _aten_add = None

    # store inferred in_idx/out_idx for modules
    in_idx_map: Dict[str, torch.Tensor] = {}
    out_idx_map: Dict[str, torch.Tensor] = {}

    for node in gm.graph.nodes:
        if node.op == "placeholder":
            continue

        # ========== call_module ==========
        if node.op == "call_module":
            name = node.target
            m = mods[name]
            in_sp = _sp(node.args[0]) if node.args else None
            in_keep = _ki(node.args[0]) if node.args and isinstance(node.args[0], fx.Node) else None

            out_meta = _get_shape(node)
            if in_sp is None:
                spec[node] = Spec(shape=out_meta or (0,), c_axis=None)
                kidx[node] = None
                continue

            # Conv / ConvTranspose
            if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                              nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)):
                # input keep idx (original)
                if in_keep is None:
                    Cin0 = int(in_sp.shape[1])
                    in_keep = _full_idx(Cin0, device=device)

                # output keep idx (original)
                out0 = int(m.out_channels)
                out_keep = keep_out_idx.get(name, _full_idx(out0, device=device))

                in_idx_map[name] = in_keep
                out_idx_map[name] = out_keep

                # update spec/node keep
                if out_meta is None:
                    # best-effort: preserve spatial from input meta
                    if len(in_sp.shape) == 4:
                        N, _, H, W = in_sp.shape
                        spec[node] = Spec(shape=(N, out0, H, W), c_axis=1)
                    else:
                        spec[node] = Spec(shape=tuple(in_sp.shape), c_axis=in_sp.c_axis)
                else:
                    out_list = list(out_meta)
                    if len(out_list) >= 2:
                        out_list[1] = out0
                    spec[node] = Spec(shape=tuple(out_list), c_axis=1)

                kidx[node] = out_keep
                continue

            # Linear
            if isinstance(m, nn.Linear):
                # input keep idx is on last dim (feature axis)
                if in_keep is None:
                    Fin0 = int(in_sp.shape[-1])
                    in_keep = _full_idx(Fin0, device=device)

                out0 = int(m.out_features)
                out_keep = keep_out_idx.get(name, _full_idx(out0, device=device))

                in_idx_map[name] = in_keep
                out_idx_map[name] = out_keep

                out_shape = list(in_sp.shape)
                out_shape[-1] = out0
                spec[node] = Spec(shape=tuple(out_shape), c_axis=_default_c_axis(tuple(out_shape)))
                kidx[node] = out_keep
                continue

            # BN/GN: preserve channel dim, keep idx same as input
            if isinstance(m, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.GroupNorm)):
                spec[node] = Spec(shape=in_sp.shape, c_axis=in_sp.c_axis)
                kidx[node] = in_keep
                if in_keep is not None:
                    in_idx_map[name] = in_keep  # for copying BN/GN params
                continue

            # Flatten module
            if isinstance(m, nn.Flatten):
                # common: NCHW -> N, C*H*W
                out_meta = _get_shape(node)
                if out_meta is not None:
                    spec[node] = Spec(shape=out_meta, c_axis=_default_c_axis(out_meta))
                else:
                    # fallback: flatten from dim=1
                    N = in_sp.shape[0]
                    feat = 1
                    for d in in_sp.shape[1:]:
                        feat *= int(d)
                    spec[node] = Spec(shape=(N, feat), c_axis=1)

                # expand keep idx if we flattened channel+spatial
                if in_keep is not None and len(in_sp.shape) == 4:
                    _, _, H, W = in_sp.shape
                    kidx[node] = _expand_channel_idx_to_flat_features(in_keep, int(H * W))
                else:
                    kidx[node] = None
                continue

            # common passthrough modules
            if isinstance(m, (nn.ReLU, nn.ReLU6, nn.GELU, nn.SiLU, nn.Sigmoid, nn.Tanh,
                              nn.Dropout, nn.Dropout2d, nn.Dropout3d, nn.Identity,
                              nn.MaxPool2d, nn.AvgPool2d, nn.AdaptiveAvgPool2d, nn.Upsample)):
                spec[node] = Spec(shape=out_meta or in_sp.shape, c_axis=in_sp.c_axis)
                kidx[node] = in_keep
                continue

            # fallback
            spec[node] = Spec(shape=out_meta or in_sp.shape, c_axis=in_sp.c_axis)
            kidx[node] = in_keep
            continue

        # ========== call_function ==========
        if node.op == "call_function":

            # torch.flatten
            if node.target is torch.flatten:
                x = node.args[0]
                in_sp = _sp(x); in_keep = _ki(x)
                out_meta = _get_shape(node)
                if in_sp is None:
                    spec[node] = Spec(shape=out_meta or (0,), c_axis=None)
                    kidx[node] = None
                    continue

                if out_meta is not None:
                    spec[node] = Spec(shape=out_meta, c_axis=_default_c_axis(out_meta))
                else:
                    # fallback flatten all except batch
                    N = in_sp.shape[0]
                    feat = 1
                    for d in in_sp.shape[1:]:
                        feat *= int(d)
                    spec[node] = Spec(shape=(N, feat), c_axis=1)

                if in_keep is not None and len(in_sp.shape) == 4:
                    _, _, H, W = in_sp.shape
                    kidx[node] = _expand_channel_idx_to_flat_features(in_keep, int(H * W))
                else:
                    kidx[node] = None
                continue

            # add / aten.add
            if node.target in (operator.add, torch.add) or (_aten_add is not None and node.target is _aten_add):
                a, b = node.args[0], node.args[1]
                sa, sb, so = _get_shape(a), _get_shape(b), _get_shape(node)
                in_sp = _sp(a); in_keep = _ki(a)
                if in_sp is None:
                    spec[node] = Spec(shape=so or (0,), c_axis=None)
                    kidx[node] = None
                    continue
                spec[node] = Spec(shape=so or in_sp.shape, c_axis=in_sp.c_axis)
                # if mismatch, choose deterministic subset
                ka, kb = _ki(a), _ki(b)
                if ka is None or kb is None:
                    kidx[node] = ka
                else:
                    if ka.numel() != kb.numel() or not torch.equal(torch.sort(ka).values, torch.sort(kb).values):
                        # choose intersection if possible, else take first min length of ka
                        inter = sorted(set(ka.tolist()).intersection(set(kb.tolist())))
                        if len(inter) >= min(ka.numel(), kb.numel()):
                            kidx[node] = torch.tensor(inter[:min(ka.numel(), kb.numel())], dtype=torch.long, device=device)
                        else:
                            kidx[node] = ka[:min(ka.numel(), kb.numel())]
                    else:
                        kidx[node] = ka
                continue

            # cat
            if node.target is torch.cat:
                tensors = node.args[0] if node.args else None
                dim = node.args[1] if len(node.args) > 1 else node.kwargs.get("dim", 0)
                dim = int(dim)

                if not isinstance(tensors, (list, tuple)):
                    spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                    kidx[node] = None
                    continue

                sps = [_sp(t) for t in tensors]
                kis = [_ki(t) for t in tensors]
                out_meta = _get_shape(node)
                if out_meta is not None:
                    spec[node] = Spec(shape=out_meta, c_axis=_default_c_axis(out_meta))
                else:
                    spec[node] = Spec(shape=(0,), c_axis=None)

                # if cat along channel axis -> concat indices with original offsets
                if sps and sps[0] is not None and spec[node].c_axis is not None:
                    rank = len(sps[0].shape)
                    dd = dim if dim >= 0 else dim + rank
                    cax = spec[node].c_axis
                    if cax < 0:
                        cax = rank + cax

                    if dd == cax:
                        # offsets are ORIGINAL channel sizes of each input (from meta)
                        offsets = []
                        off = 0
                        for t in tensors:
                            sh = _get_shape(t)  # original shape
                            if sh is None:
                                # fallback: cannot compute offsets robustly
                                offsets = None
                                break
                            offsets.append(off)
                            off += int(sh[cax])
                        if offsets is None or any(k is None for k in kis):
                            kidx[node] = None
                        else:
                            out_list = []
                            for k, off in zip(kis, offsets):
                                out_list.append((k + off).to(device))
                            kidx[node] = torch.cat(out_list, dim=0)
                    else:
                        # cat along non-channel dim: channel idx should be same as first
                        kidx[node] = kis[0]
                else:
                    kidx[node] = None
                continue

            # relu
            if node.target in (torch.relu, torch.nn.functional.relu):
                x = node.args[0]
                spec[node] = Spec(shape=_get_shape(node) or (_sp(x).shape if _sp(x) else (0,)), c_axis=_sp(x).c_axis if _sp(x) else None)
                kidx[node] = _ki(x)
                continue

            # fallback: passthrough
            x0 = node.args[0] if node.args else None
            spec[node] = Spec(shape=_get_shape(node) or (_sp(x0).shape if _sp(x0) else (0,)), c_axis=_sp(x0).c_axis if _sp(x0) else None)
            kidx[node] = _ki(x0) if isinstance(x0, fx.Node) else None
            continue

        # ========== call_method ==========
        if node.op == "call_method":
            method = node.target
            x0 = node.args[0]
            in_sp = _sp(x0); in_keep = _ki(x0)
            out_meta = _get_shape(node)

            if in_sp is None:
                spec[node] = Spec(shape=out_meta or (0,), c_axis=None)
                kidx[node] = None
                continue

            if method in ("view", "reshape"):
                # only support common view(N, -1) or reshape(N, -1)
                new_shape = node.args[1:]
                if len(new_shape) == 2 and isinstance(new_shape[0], fx.Node) and int(new_shape[1]) == -1:
                    spec[node] = Spec(shape=out_meta, c_axis=_default_c_axis(out_meta)) if out_meta else Spec(shape=(in_sp.shape[0], -1), c_axis=1)
                    kidx[node] = in_keep  # assume already feature idx
                else:
                    if strict:
                        raise RuntimeError(f"[UNSUPPORTED] view/reshape pattern: {new_shape}")
                    spec[node] = Spec(shape=out_meta or in_sp.shape, c_axis=_default_c_axis(out_meta) if out_meta else in_sp.c_axis)
                    kidx[node] = None
                continue

            if method == "flatten":
                # treat like flatten
                spec[node] = Spec(shape=out_meta or in_sp.shape, c_axis=_default_c_axis(out_meta) if out_meta else in_sp.c_axis)
                if in_keep is not None and len(in_sp.shape) == 4 and out_meta is not None and len(out_meta) == 2:
                    _, _, H, W = in_sp.shape
                    kidx[node] = _expand_channel_idx_to_flat_features(in_keep, int(H * W))
                else:
                    kidx[node] = in_keep
                continue

            if method in ("add", "__add__", "__iadd__"):
                b = node.args[1]
                kb = _ki(b)
                spec[node] = Spec(shape=out_meta or in_sp.shape, c_axis=in_sp.c_axis)
                if in_keep is None or kb is None:
                    kidx[node] = in_keep
                else:
                    kidx[node] = in_keep if in_keep.numel() <= kb.numel() else kb
                continue

            # default passthrough
            spec[node] = Spec(shape=out_meta or in_sp.shape, c_axis=in_sp.c_axis)
            kidx[node] = in_keep
            continue

        if node.op == "output":
            break

    # -------------------------
    # Now actually copy weights
    # -------------------------
    o_mods = dict(original_model.named_modules())
    p_mods = dict(pruned_model.named_modules())

    def _copy_conv_like(name: str, m_old: nn.Module, m_new: nn.Module):
        W_old = m_old.weight.data
        W_new = m_new.weight.data

        g = int(getattr(m_old, "groups", 1))
        if _is_depthwise_conv(m_old):
            # depthwise: weight shape [Cout, 1, k, k], only need out_idx
            out_idx = out_idx_map.get(name, _full_idx(W_old.shape[0], device=device))
            out_idx = out_idx.to(device)
            out_idx = out_idx[:W_new.shape[0]]
            sliced = W_old.index_select(0, out_idx)
            if sliced.shape != W_new.shape:
                # fallback: truncate/pad not allowed -> strict
                if strict:
                    raise RuntimeError(f"{name} depthwise weight shape mismatch: {sliced.shape} vs {W_new.shape}")
                sliced = sliced[:W_new.shape[0]]
            W_new.copy_(sliced)
        elif g == 1:
            in_idx = in_idx_map.get(name, _full_idx(W_old.shape[1], device=device)).to(device)
            out_idx = out_idx_map.get(name, _full_idx(W_old.shape[0], device=device)).to(device)

            in_idx = in_idx[:W_new.shape[1]]
            out_idx = out_idx[:W_new.shape[0]]

            sliced = W_old.index_select(0, out_idx).index_select(1, in_idx)
            if sliced.shape != W_new.shape:
                if strict:
                    raise RuntimeError(f"{name} conv weight shape mismatch: {sliced.shape} vs {W_new.shape}")
            W_new.copy_(sliced)
        else:
            # grouped conv (non-depthwise): best-effort group-wise contiguous selection
            Cin0 = int(m_old.in_channels)
            Cout0 = int(m_old.out_channels)
            Cin_pg = Cin0 // g
            Cout_pg = Cout0 // g
            Cin_new = int(getattr(m_new, "in_channels"))
            Cout_new = int(getattr(m_new, "out_channels"))
            Cin_new_pg = Cin_new // g
            Cout_new_pg = Cout_new // g

            # pick first Cin_new_pg per group, first Cout_new_pg per group
            # (this is the most universal safe mapping)
            Wg = []
            for gg in range(g):
                o_start = gg * Cout_pg
                i_start = gg * Cin_pg
                o_sel = torch.arange(o_start, o_start + Cout_new_pg, dtype=torch.long, device=device)
                i_sel_local = torch.arange(0, Cin_new_pg, dtype=torch.long, device=device)
                # weight dim1 is per-group input channels
                part = W_old.index_select(0, o_sel).index_select(1, i_sel_local)
                Wg.append(part)
            sliced = torch.cat(Wg, dim=0)
            if sliced.shape != W_new.shape and strict:
                raise RuntimeError(f"{name} grouped conv weight shape mismatch: {sliced.shape} vs {W_new.shape}")
            W_new.copy_(sliced)

        # bias
        if getattr(m_old, "bias", None) is not None and getattr(m_new, "bias", None) is not None:
            b_old = m_old.bias.data
            b_new = m_new.bias.data
            out_idx = out_idx_map.get(name, _full_idx(b_old.shape[0], device=device)).to(device)
            out_idx = out_idx[:b_new.shape[0]]
            b_new.copy_(b_old.index_select(0, out_idx))

    def _copy_linear(name: str, m_old: nn.Linear, m_new: nn.Linear):
        W_old = m_old.weight.data
        W_new = m_new.weight.data

        in_idx = in_idx_map.get(name, _full_idx(W_old.shape[1], device=device)).to(device)
        out_idx = out_idx_map.get(name, _full_idx(W_old.shape[0], device=device)).to(device)

        in_idx = in_idx[:W_new.shape[1]]
        out_idx = out_idx[:W_new.shape[0]]

        sliced = W_old.index_select(0, out_idx).index_select(1, in_idx)
        if sliced.shape != W_new.shape and strict:
            raise RuntimeError(f"{name} linear weight shape mismatch: {sliced.shape} vs {W_new.shape}")
        W_new.copy_(sliced)

        if m_old.bias is not None and m_new.bias is not None:
            b_old = m_old.bias.data
            b_new = m_new.bias.data
            b_new.copy_(b_old.index_select(0, out_idx))

    def _copy_norm_1d(name: str, m_old: nn.Module, m_new: nn.Module):
        # BN/GN: weight,bias,running stats along channel dim
        idx = in_idx_map.get(name, None)
        if idx is None:
            return
        idx = idx.to(device)
        # weight/bias
        for attr in ("weight", "bias"):
            if hasattr(m_old, attr) and hasattr(m_new, attr):
                t_old = getattr(m_old, attr)
                t_new = getattr(m_new, attr)
                if t_old is not None and t_new is not None and t_old.data.ndim == 1:
                    idx2 = idx[:t_new.data.shape[0]]
                    t_new.data.copy_(t_old.data.index_select(0, idx2))
        # running stats
        for attr in ("running_mean", "running_var"):
            if hasattr(m_old, attr) and hasattr(m_new, attr):
                t_old = getattr(m_old, attr)
                t_new = getattr(m_new, attr)
                if isinstance(t_old, torch.Tensor) and isinstance(t_new, torch.Tensor) and t_old.ndim == 1:
                    idx2 = idx[:t_new.shape[0]]
                    t_new.copy_(t_old.index_select(0, idx2))

    # iterate pruned modules and copy
    for name, m_new in p_mods.items():
        if name not in o_mods:
            continue
        m_old = o_mods[name]

        if isinstance(m_new, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                              nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)) and \
           isinstance(m_old, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                              nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)):
            _copy_conv_like(name, m_old, m_new)

        elif isinstance(m_new, nn.Linear) and isinstance(m_old, nn.Linear):
            _copy_linear(name, m_old, m_new)

        elif isinstance(m_new, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.GroupNorm)) and \
             isinstance(m_old, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.GroupNorm)):
            _copy_norm_1d(name, m_old, m_new)

        else:
            # for other modules, if state_dict shapes match, we can copy directly (optional)
            pass

    return pruned_model


# =========================
# Wrapper similar to your original function
# =========================

def Generate_model_after_pruning(
    pruned_model: nn.Module,                 # already slimmed structure (your universal slimming output)
    original_model: nn.Module,
    pruned_model_save_path: str,
    results: Dict[str, Any],
    k_list: List[int],
    the_list_of_layers_to_prune: List[int],  # indices in original_model.named_modules()
    example_inputs: Union[torch.Tensor, Tuple[torch.Tensor, ...]],
    finetune_pruned: bool = False,
    finetune_epochs: int = 10,
    finetunedata=None,
    valdata=None,
    device: str = "cuda",
    verbose: bool = True,
):
    pruned_model = pruned_model.to(device).eval()
    original_model = original_model.to(device).eval()

    keep_out = build_keep_out_idx_map_from_results(
        original_model=original_model,
        the_list_of_layers_to_prune=the_list_of_layers_to_prune,
        k_list=k_list,
        results=results,
        key_fmt="D_{j}_s2b_idx",
        device="cpu",
    )

    pruned_model = copy_params_to_pruned_model_fx(
        original_model=original_model,
        pruned_model=pruned_model,
        keep_out_idx=keep_out,
        example_inputs=example_inputs,
        align_add=True,
        verbose=verbose,
        strict=True,
    )

    # report
    n_pruned = sum(p.numel() for p in pruned_model.parameters() if p.requires_grad)
    n_orig = sum(p.numel() for p in original_model.parameters() if p.requires_grad)
    report = {
        "parameters number": n_pruned,
        "pruning rate": 1.0 - (n_pruned / max(1, n_orig)),
    }
    if verbose:
        print(f'parameters number: {report["parameters number"]}')
        print(f'pruning rate: {report["pruning rate"]}')

    # optional finetune (keep your own finetune_model)
    if finetune_pruned:
        pruned_model = finetune_model(
            model=pruned_model,
            train_loader=finetunedata,
            val_loader=valdata,
            epochs=finetune_epochs,
            lr=0.001,
            momentum=0.9,
            weight_decay=1e-4,
            device=device,
            grad_clip_norm=None,
            amp=True,
            log_every=100,
        )

    # ✅ 强烈建议保存 state_dict，避免 PyTorch2.6 的 weights_only 安全限制
    torch.save(pruned_model.state_dict(), pruned_model_save_path)

    return pruned_model, report

###############################################################################
#得到剪枝后的模型架构
import copy
import math
import operator
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Union, Any
from collections import deque

import torch
import torch.nn as nn
import torch.fx as fx
from torch.fx.passes.shape_prop import ShapeProp


# =========================
# Shape spec
# =========================

@dataclass
class Spec:
    shape: Tuple[int, ...]
    c_axis: Optional[int]  # NCHW->1, (N,F)->1, (N,T,C)->-1


def _get_shape(node: fx.Node) -> Optional[Tuple[int, ...]]:
    tm = node.meta.get("tensor_meta", None)
    if tm is None:
        return None
    shp = getattr(tm, "shape", None)
    if shp is None:
        return None
    return tuple(int(x) for x in shp)


def _default_c_axis(shape: Tuple[int, ...]) -> Optional[int]:
    if len(shape) == 4:
        return 1
    if len(shape) == 2:
        return 1
    if len(shape) == 3:
        return -1
    return None


def _pair(x):
    return x if isinstance(x, tuple) else (x, x)


def _is_depthwise_conv(m: nn.Module) -> bool:
    return isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d)) and (m.groups == m.in_channels == m.out_channels)


def _set_submodule(model: nn.Module, path: str, new_module: nn.Module):
    parts = path.split(".")
    parent = model
    for p in parts[:-1]:
        parent = getattr(parent, p)
    setattr(parent, parts[-1], new_module)


def _infer_flatten_shape(in_shape: Tuple[int, ...], start_dim: int, end_dim: int) -> Tuple[int, ...]:
    shp = list(in_shape)
    nd = len(shp)
    if end_dim < 0:
        end_dim += nd
    left = shp[:start_dim]
    mid = shp[start_dim:end_dim + 1]
    right = shp[end_dim + 1:]
    prod = 1
    for v in mid:
        prod *= int(v)
    return tuple(left + [prod] + right)


def _infer_view_shape(in_shape: Tuple[int, ...], new_shape_raw: Tuple[Any, ...]) -> Tuple[int, ...]:
    new_shape: List[int] = []
    for i, d in enumerate(new_shape_raw):
        if isinstance(d, int):
            new_shape.append(d)
        elif isinstance(d, fx.Node):
            if i == 0:
                new_shape.append(int(in_shape[0]))  # batch
            else:
                raise RuntimeError(
                    "view/reshape 形状包含动态 Node（非 batch 维），建议用 torch.flatten(x,1) 或 view(x.size(0), -1)。"
                )
        else:
            raise RuntimeError("view/reshape 形状参数不是 int/-1/Node(batch)，无法推导。")

    total = math.prod([int(v) for v in in_shape])

    known = 1
    minus1 = None
    for i, d in enumerate(new_shape):
        if d == -1:
            if minus1 is not None:
                raise RuntimeError("view/reshape 出现多个 -1，无法推导。")
            minus1 = i
        else:
            known *= d

    if minus1 is not None:
        if known == 0 or total % known != 0:
            raise RuntimeError(f"view/reshape 无法推导 -1：in={in_shape}, target={tuple(new_shape)}")
        new_shape[minus1] = total // known

    if math.prod(new_shape) != total:
        raise RuntimeError(
            f"view/reshape 元素数不匹配：in={in_shape} numel={total}, target={tuple(new_shape)} numel={math.prod(new_shape)}。"
            f"常见原因：你写死了某维，剪枝后不成立。"
        )
    return tuple(int(x) for x in new_shape)


def _gcd_group_adjust(num_groups: int, num_channels: int) -> int:
    g = min(int(num_groups), int(num_channels))
    while g > 1 and (num_channels % g != 0):
        g -= 1
    return max(1, g)


def _outdim_of(m: nn.Module) -> int:
    if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                      nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)):
        return int(m.out_channels)
    if isinstance(m, nn.Linear):
        return int(m.out_features)
    raise TypeError(type(m).__name__)


# =========================
# FX arg/kwarg helpers
# =========================

def _fx_get(node: fx.Node, arg_i: int, kw: str, default=None):
    if len(node.args) > arg_i:
        return node.args[arg_i]
    if kw in node.kwargs:
        return node.kwargs[kw]
    return default


def _fx_get_int(node: fx.Node, arg_i: int, kw: str, default: int) -> int:
    v = _fx_get(node, arg_i, kw, default)
    return int(v)


# =========================
# Conv / ConvTranspose output-shape
# =========================

def _conv_out_shape(in_sp: Spec, orig_out: Optional[Tuple[int, ...]], new_out_channels: int, conv: nn.Module) -> Spec:
    N = int(in_sp.shape[0])

    if orig_out is not None and len(orig_out) == len(in_sp.shape):
        out_list = list(orig_out)
        out_list[0] = N
        out_list[1] = int(new_out_channels)
        return Spec(shape=tuple(int(x) for x in out_list), c_axis=1)

    # no meta -> formula
    if isinstance(conv, nn.Conv1d):
        _, _, L = in_sp.shape
        k = conv.kernel_size[0]; s = conv.stride[0]; p = conv.padding[0]; d = conv.dilation[0]
        L2 = math.floor((L + 2*p - d*(k-1) - 1)/s + 1)
        return Spec(shape=(N, int(new_out_channels), int(L2)), c_axis=1)

    if isinstance(conv, nn.Conv2d):
        _, _, H, W = in_sp.shape
        kh, kw = _pair(conv.kernel_size); sh, sw = _pair(conv.stride); ph, pw = _pair(conv.padding); dh, dw = _pair(conv.dilation)
        H2 = math.floor((H + 2*ph - dh*(kh-1) - 1)/sh + 1)
        W2 = math.floor((W + 2*pw - dw*(kw-1) - 1)/sw + 1)
        return Spec(shape=(N, int(new_out_channels), int(H2), int(W2)), c_axis=1)

    if isinstance(conv, nn.ConvTranspose2d):
        _, _, H, W = in_sp.shape
        kh, kw = _pair(conv.kernel_size); sh, sw = _pair(conv.stride); ph, pw = _pair(conv.padding); dh, dw = _pair(conv.dilation)
        oph, opw = _pair(conv.output_padding)
        H2 = (H - 1)*sh - 2*ph + dh*(kh-1) + oph + 1
        W2 = (W - 1)*sw - 2*pw + dw*(kw-1) + opw + 1
        return Spec(shape=(N, int(new_out_channels), int(H2), int(W2)), c_axis=1)

    raise RuntimeError(f"Conv shape formula not implemented for {type(conv).__name__}, please rely on shape meta.")


# =========================
# Fallback: ops that preserve channel/feature dim
# =========================

def _adapt_out_shape_preserve_channel(in_sp: Spec, orig_in: Optional[Tuple[int, ...]], orig_out: Optional[Tuple[int, ...]]) -> Spec:
    if orig_in is None or orig_out is None:
        return Spec(shape=in_sp.shape, c_axis=_default_c_axis(in_sp.shape))

    if len(orig_in) != len(orig_out):
        raise RuntimeError(f"[UNSUPPORTED] rank changed: {orig_in} -> {orig_out} (need handler like flatten/view/reshape).")

    out_list = list(orig_out)
    cax = in_sp.c_axis if in_sp.c_axis is not None else _default_c_axis(in_sp.shape)
    if cax is None:
        return Spec(shape=tuple(out_list), c_axis=None)
    if cax < 0:
        cax = len(out_list) + cax

    if orig_in[cax] != orig_out[cax]:
        raise RuntimeError(f"[UNSUPPORTED] channel/feature dim changed: {orig_in} -> {orig_out} (need handler).")

    out_list[cax] = in_sp.shape[cax]
    out_shape = tuple(int(x) for x in out_list)
    return Spec(shape=out_shape, c_axis=in_sp.c_axis if in_sp.c_axis is not None else _default_c_axis(out_shape))


# =========================
# Residual add alignment (少剪不多剪)
# =========================

class _UF:
    def __init__(self):
        self.p = {}
    def find(self, x):
        if x not in self.p:
            self.p[x] = x
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra
    def groups(self):
        g = {}
        for x in list(self.p.keys()):
            r = self.find(x)
            g.setdefault(r, []).append(x)
        return list(g.values())


# ✅ 新版：BFS 追溯最近 Conv/Linear（能穿透 add/cat/getitem/BN/ReLU/reshape/flatten 等）
def _trace_channel_source(node: fx.Node, gm: fx.GraphModule) -> Optional[str]:
    modules = dict(gm.named_modules())
    q = deque([node])
    visited = set()

    def push(v):
        if isinstance(v, fx.Node):
            q.append(v)
        elif isinstance(v, (list, tuple)):
            for vv in v:
                push(vv)

    while q:
        cur = q.popleft()
        if not isinstance(cur, fx.Node) or cur in visited:
            continue
        visited.add(cur)

        if cur.op == "call_module":
            m = modules.get(cur.target, None)
            if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                              nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d,
                              nn.Linear)):
                return cur.target
            # 继续穿透其第一个 tensor 输入
            if cur.args:
                push(cur.args[0])
            continue

        if cur.op == "call_function":
            # 统一穿透所有 args（非 Node 会被忽略）
            for a in cur.args:
                push(a)
            for a in cur.kwargs.values():
                push(a)
            continue

        if cur.op == "call_method":
            # x.view/reshape/flatten/permute/... 统一穿透第一个输入
            if cur.args:
                push(cur.args[0])
            continue

        # placeholder/output -> stop
    return None


# ✅ 新版：对所有 residual add 建约束，按“少剪不多剪”对齐
def _align_keep_for_add(model: nn.Module, keep_cnt: Dict[str, int], example_inputs: Tuple[torch.Tensor, ...], verbose: bool):
    gm = fx.symbolic_trace(model)
    ShapeProp(gm).propagate(*example_inputs)
    mods = dict(gm.named_modules())
    uf = _UF()

    # 兼容 aten.add 形式（不同 pytorch 版本会出现）
    _aten_add = None
    try:
        _aten_add = torch.ops.aten.add.Tensor
    except Exception:
        _aten_add = None

    def is_add_node(n: fx.Node) -> bool:
        if n.op == "call_function" and n.target in {operator.add, torch.add}:
            return True
        if _aten_add is not None and n.op == "call_function" and n.target is _aten_add:
            return True
        if n.op == "call_method" and n.target in ("add", "__add__", "__iadd__"):
            return True
        return False

    def get_add_args(n: fx.Node):
        if n.op == "call_method":
            # x.add(y) / x.__add__(y)
            return n.args[0], n.args[1]
        else:
            return n.args[0], n.args[1]

    for node in gm.graph.nodes:
        if not is_add_node(node):
            continue
        if len(node.args) < 2:
            continue
        a, b = get_add_args(node)
        if not isinstance(a, fx.Node) or not isinstance(b, fx.Node):
            continue
        sa, sb, so = _get_shape(a), _get_shape(b), _get_shape(node)
        if sa is None or sb is None or so is None:
            continue
        # 只处理真正 residual：两边 shape 完全一致
        if sa != sb or sa != so:
            continue

        src_a = _trace_channel_source(a, gm)
        src_b = _trace_channel_source(b, gm)
        if src_a is None or src_b is None:
            continue

        ma, mb = mods.get(src_a), mods.get(src_b)
        if ma is None or mb is None:
            continue

        if _outdim_of(ma) != _outdim_of(mb):
            # 这里一般意味着不是“通道同维”的残差，或 trace 追到了不该追的模块
            # 先跳过，不硬报错（提高覆盖率）
            continue

        uf.union(src_a, src_b)

    aligned = dict(keep_cnt)
    for group in uf.groups():
        # 组内所有模块 outdim 本应一致（残差 add）
        out0 = _outdim_of(mods[group[0]])
        keeps = []
        for nm in group:
            # 若该 nm 本来没剪，就默认 keep=原始 outdim（保证少剪不多剪能把剪多的抬回去）
            keeps.append(aligned.get(nm, _outdim_of(mods[nm])))
        keep_final = max(keeps)
        keep_final = max(1, min(out0, keep_final))

        changed = False
        for nm in group:
            if nm in aligned and aligned[nm] != keep_final:
                aligned[nm] = keep_final
                changed = True

        if verbose and changed:
            print(f"[add-align] {group}: keep {keeps} -> {keep_final}")

    return aligned


# =========================
# Main API
# =========================

def pruned_structure(
    model: nn.Module,
    named_modules_indices: List[int],
    k_list: List[int],
    example_inputs: Union[torch.Tensor, Tuple[torch.Tensor, ...]],
    align_residual_add: bool = True,
    verbose: bool = True,
    strict_forward_check: bool = True,
) -> nn.Module:
    assert len(named_modules_indices) == len(k_list)

    device = next(model.parameters()).device if any(True for _ in model.parameters()) else torch.device("cpu")
    model = model.to(device).eval()

    if isinstance(example_inputs, torch.Tensor):
        example_inputs = (example_inputs,)
    example_inputs = tuple(t.to(device) for t in example_inputs)

    named = list(model.named_modules())
    mods = dict(model.named_modules())

    # keep plan
    keep_cnt: Dict[str, int] = {}
    for idx, k in zip(named_modules_indices, k_list):
        path, m = named[idx]
        if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                          nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)):
            out = int(m.out_channels)
            keep = max(1, out - int(k))
            keep_cnt[path] = keep
            if verbose:
                print(f"[plan] {idx:4d}  {path:<40}  {type(m).__name__:<18} out {out} -> {keep}")
        elif isinstance(m, nn.Linear):
            out = int(m.out_features)
            keep = max(1, out - int(k))
            keep_cnt[path] = keep
            if verbose:
                print(f"[plan] {idx:4d}  {path:<40}  Linear               out {out} -> {keep}")
        else:
            raise RuntimeError(f"Index {idx} is not Conv/Linear: {path} -> {type(m).__name__}")

    # residual add align
    if align_residual_add:
        keep_cnt = _align_keep_for_add(model, keep_cnt, example_inputs, verbose=verbose)

    # trace original
    gm = fx.symbolic_trace(model)
    ShapeProp(gm).propagate(*example_inputs)

    # clone and rewrite
    new_model = copy.deepcopy(model).to(device).eval()
    spec: Dict[fx.Node, Spec] = {}

    placeholders = [n for n in gm.graph.nodes if n.op == "placeholder"]
    if len(placeholders) != len(example_inputs):
        raise RuntimeError("example_inputs 数量与 forward 输入不一致")
    for n, t in zip(placeholders, example_inputs):
        shp = tuple(int(x) for x in t.shape)
        spec[n] = Spec(shape=shp, c_axis=_default_c_axis(shp))

    def _sp(x) -> Optional[Spec]:
        return spec.get(x, None) if isinstance(x, fx.Node) else None

    # 兼容 aten.add
    _aten_add = None
    try:
        _aten_add = torch.ops.aten.add.Tensor
    except Exception:
        _aten_add = None

    for node in gm.graph.nodes:
        if node.op == "placeholder":
            continue

        # ========== call_module ==========
        if node.op == "call_module":
            name = node.target
            m_old = mods[name]
            in_sp = _sp(node.args[0]) if node.args else None
            if in_sp is None:
                spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                continue

            # Conv / ConvTranspose
            if isinstance(m_old, (nn.Conv1d, nn.Conv2d, nn.Conv3d,
                                  nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)):
                Cin = int(in_sp.shape[1])
                groups = int(getattr(m_old, "groups", 1))

                # depthwise conv：不能单独剪 out，只能跟随 Cin
                if isinstance(m_old, (nn.Conv1d, nn.Conv2d, nn.Conv3d)) and _is_depthwise_conv(m_old):
                    new_in, new_out, new_groups = Cin, Cin, Cin
                    if name in keep_cnt and verbose:
                        print(f"[warn] {name}: depthwise conv 忽略 out 剪枝，强制 out=in={Cin}")
                else:
                    new_in = Cin
                    out0 = int(m_old.out_channels)
                    new_out_req = int(keep_cnt.get(name, out0))
                    new_out_req = max(1, min(out0, new_out_req))

                    # 非 depthwise grouped conv 的一致性要求
                    if isinstance(m_old, (nn.Conv1d, nn.Conv2d, nn.Conv3d)) and groups > 1:
                        if new_in % groups != 0:
                            raise RuntimeError(f"{name}: grouped conv 需要 in%groups==0，但 in={new_in}, groups={groups}")
                        new_out = min(out0, ((new_out_req + groups - 1)//groups)*groups)
                        if new_out != new_out_req and verbose:
                            print(f"[warn] {name}: grouped conv out {new_out_req} -> {new_out} (align groups={groups})")
                    else:
                        new_out = new_out_req

                    new_groups = groups

                ConvCls = type(m_old)
                kwargs = dict(
                    in_channels=int(new_in),
                    out_channels=int(new_out),
                    kernel_size=m_old.kernel_size,
                    stride=m_old.stride,
                    padding=m_old.padding,
                    dilation=m_old.dilation,
                    groups=int(new_groups),
                    bias=(m_old.bias is not None),
                )
                if isinstance(m_old, (nn.ConvTranspose1d, nn.ConvTranspose2d, nn.ConvTranspose3d)):
                    kwargs["output_padding"] = m_old.output_padding
                conv_new = ConvCls(**kwargs).to(device)
                _set_submodule(new_model, name, conv_new)

                spec[node] = _conv_out_shape(in_sp, _get_shape(node), int(new_out), conv_new)
                continue

            # BatchNorm
            if isinstance(m_old, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
                C = int(in_sp.shape[1])
                BNCls = type(m_old)
                bn = BNCls(C, eps=m_old.eps, momentum=m_old.momentum, affine=m_old.affine,
                           track_running_stats=m_old.track_running_stats).to(device)
                _set_submodule(new_model, name, bn)
                spec[node] = Spec(shape=in_sp.shape, c_axis=1)
                continue

            # LayerNorm
            if isinstance(m_old, nn.LayerNorm):
                old_norm = m_old.normalized_shape
                n = len(old_norm) if isinstance(old_norm, tuple) else 1
                new_norm = tuple(int(x) for x in in_sp.shape[-n:])
                ln = nn.LayerNorm(new_norm, eps=m_old.eps, elementwise_affine=m_old.elementwise_affine).to(device)
                _set_submodule(new_model, name, ln)
                spec[node] = Spec(shape=in_sp.shape, c_axis=in_sp.c_axis)
                continue

            # GroupNorm
            if isinstance(m_old, nn.GroupNorm):
                C = int(in_sp.shape[1])
                g = _gcd_group_adjust(m_old.num_groups, C)
                gn = nn.GroupNorm(g, C, eps=m_old.eps, affine=m_old.affine).to(device)
                _set_submodule(new_model, name, gn)
                spec[node] = Spec(shape=in_sp.shape, c_axis=1)
                continue

            # Flatten
            if isinstance(m_old, nn.Flatten):
                out_shape = _infer_flatten_shape(in_sp.shape, int(m_old.start_dim), int(m_old.end_dim))
                spec[node] = Spec(shape=out_shape, c_axis=_default_c_axis(out_shape))
                continue

            # Linear: apply to last dim
            if isinstance(m_old, nn.Linear):
                Fin = int(in_sp.shape[-1])
                out0 = int(m_old.out_features)
                new_out = int(keep_cnt.get(name, out0))
                new_out = max(1, min(out0, new_out))
                fc = nn.Linear(Fin, new_out, bias=(m_old.bias is not None)).to(device)
                _set_submodule(new_model, name, fc)

                out_list = list(in_sp.shape)
                out_list[-1] = new_out
                out_shape = tuple(out_list)
                spec[node] = Spec(shape=out_shape, c_axis=_default_c_axis(out_shape))
                continue

            # common shape-preserving modules
            if isinstance(m_old, (nn.ReLU, nn.ReLU6, nn.GELU, nn.SiLU, nn.Sigmoid, nn.Tanh,
                                  nn.Dropout, nn.Dropout2d, nn.Dropout3d, nn.Identity,
                                  nn.MaxPool2d, nn.AvgPool2d, nn.AdaptiveAvgPool2d, nn.Upsample)):
                orig_in = _get_shape(node.args[0]) if node.args and isinstance(node.args[0], fx.Node) else None
                orig_out = _get_shape(node)
                spec[node] = _adapt_out_shape_preserve_channel(in_sp, orig_in, orig_out)
                continue

            # fallback
            orig_in = _get_shape(node.args[0]) if node.args and isinstance(node.args[0], fx.Node) else None
            orig_out = _get_shape(node)
            spec[node] = _adapt_out_shape_preserve_channel(in_sp, orig_in, orig_out)
            continue

        # ========== call_function ==========
        if node.op == "call_function":

            # torch.flatten
            if node.target is torch.flatten:
                in_sp = _sp(_fx_get(node, 0, "input", None))
                if in_sp is None:
                    spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                    continue
                start_dim = _fx_get_int(node, 1, "start_dim", 0)
                end_dim = _fx_get_int(node, 2, "end_dim", -1)
                out_shape = _infer_flatten_shape(in_sp.shape, start_dim, end_dim)
                spec[node] = Spec(shape=out_shape, c_axis=_default_c_axis(out_shape))
                continue

            # add / aten.add
            if node.target in (operator.add, torch.add) or (_aten_add is not None and node.target is _aten_add):
                a = _sp(node.args[0]); b = _sp(node.args[1])
                if a is None or b is None:
                    spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                    continue
                if a.shape != b.shape:
                    raise RuntimeError(f"add shape mismatch: {a.shape} vs {b.shape}")
                spec[node] = Spec(shape=a.shape, c_axis=a.c_axis)
                continue

            # cat  —— dim 可能在 kwargs
            if node.target is torch.cat:
                tensors = _fx_get(node, 0, "tensors", None)
                if tensors is None:
                    spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                    continue
                dim = _fx_get_int(node, 1, "dim", 0)

                sps = [_sp(t) for t in tensors]
                if any(s is None for s in sps):
                    spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                    continue

                rank = len(sps[0].shape)
                if dim < 0:
                    dim += rank
                base = list(sps[0].shape)
                base[dim] = sum(s.shape[dim] for s in sps)  # type: ignore
                out_shape = tuple(base)
                spec[node] = Spec(shape=out_shape, c_axis=_default_c_axis(out_shape))
                continue

            # permute —— dims 可能在 kwargs
            if node.target is torch.permute:
                x = _fx_get(node, 0, "input", None)
                in_sp = _sp(x)
                if in_sp is None:
                    spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                    continue
                dims_raw = _fx_get(node, 1, "dims", None)
                if dims_raw is None:
                    spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                    continue
                dims = tuple(int(d) for d in dims_raw)
                out_shape = tuple(in_sp.shape[d] for d in dims)
                spec[node] = Spec(shape=out_shape, c_axis=_default_c_axis(out_shape))
                continue

            # relu-like
            if node.target in (torch.relu, torch.nn.functional.relu):
                in_sp = _sp(node.args[0])
                spec[node] = Spec(shape=in_sp.shape, c_axis=in_sp.c_axis) if in_sp else Spec(shape=_get_shape(node) or (0,), c_axis=None)
                continue

            # default preserve-channel fallback
            in0 = node.args[0] if node.args else None
            in_sp0 = _sp(in0) if isinstance(in0, fx.Node) else None
            if in_sp0 is None:
                spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
            else:
                orig_in = _get_shape(in0) if isinstance(in0, fx.Node) else None
                orig_out = _get_shape(node)
                spec[node] = _adapt_out_shape_preserve_channel(in_sp0, orig_in, orig_out)
            continue

        # ========== call_method ==========
        if node.op == "call_method":
            method = node.target
            x0 = node.args[0]
            in_sp = _sp(x0) if isinstance(x0, fx.Node) else None
            if in_sp is None:
                spec[node] = Spec(shape=_get_shape(node) or (0,), c_axis=None)
                continue

            if method == "flatten":
                out_meta = _get_shape(node)
                if out_meta is not None:
                    spec[node] = Spec(shape=out_meta, c_axis=_default_c_axis(out_meta))
                else:
                    out_shape = _infer_flatten_shape(in_sp.shape, 1, -1)
                    spec[node] = Spec(shape=out_shape, c_axis=_default_c_axis(out_shape))
                continue

            if method in ("view", "reshape"):
                new_shape_raw = tuple(node.args[1:])
                out_shape = _infer_view_shape(in_sp.shape, new_shape_raw)
                spec[node] = Spec(shape=out_shape, c_axis=_default_c_axis(out_shape))
                continue

            if method == "permute":
                dims = tuple(int(d) for d in node.args[1:])
                out_shape = tuple(in_sp.shape[d] for d in dims)
                spec[node] = Spec(shape=out_shape, c_axis=_default_c_axis(out_shape))
                continue

            if method == "transpose":
                d0 = int(node.args[1]); d1 = int(node.args[2])
                shp = list(in_sp.shape)
                shp[d0], shp[d1] = shp[d1], shp[d0]
                spec[node] = Spec(shape=tuple(shp), c_axis=_default_c_axis(tuple(shp)))
                continue

            if method in ("add", "__add__", "__iadd__"):
                # x.add(y)
                b = _sp(node.args[1]) if len(node.args) > 1 and isinstance(node.args[1], fx.Node) else None
                if b is None:
                    spec[node] = Spec(shape=_get_shape(node) or in_sp.shape, c_axis=in_sp.c_axis)
                    continue
                if in_sp.shape != b.shape:
                    raise RuntimeError(f"add(method) shape mismatch: {in_sp.shape} vs {b.shape}")
                spec[node] = Spec(shape=in_sp.shape, c_axis=in_sp.c_axis)
                continue

            # default
            orig_in = _get_shape(x0) if isinstance(x0, fx.Node) else None
            orig_out = _get_shape(node)
            spec[node] = _adapt_out_shape_preserve_channel(in_sp, orig_in, orig_out)
            continue

        if node.op == "output":
            break

    if strict_forward_check:
        with torch.no_grad():
            _ = new_model(*example_inputs)

    return new_model

###############################################################################
if __name__ == '__main__':
    model_path = r'C:\Users\Administrator\PycharmProjects\lcq\Data\CIFAR10_vgg16.pht'
    data_path =  r'C:\Users\Administrator\PycharmProjects\lcq\DataSet\cifar10_prune_dataset.pkl'
    with open(data_path, 'rb') as f:
        prune_datasetloader = pickle.load(f)
    from torch.utils.data import DataLoader, Subset

    indices = list(range(64))
    subset = Subset(prune_datasetloader.dataset, indices)
    prune_datasetloader = DataLoader(
        subset,
        batch_size=prune_datasetloader.batch_size,  # 想改可改
        shuffle=False,  # 小样本一般不再 shuffle
    )
    fortestfinetunedata = prune_datasetloader
    fortestvaldata = prune_datasetloader
    model = torch.load(model_path)
    results_save_path = 'test_res.pkl'
    the_list_of_layers_to_prune = [2,4,7,9,12,14,16,19,21,23,26,28,30,35,38]#]
    the_list_of_layers_to_compute_Distance = [3,5,8,10,13,15,17,20,22,24,27,29,31,36,39]#]
    loss_function = nn.CrossEntropyLoss()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    class_num = 10
    results = FAIR_Pruner_get_results(model, prune_datasetloader, results_save_path, the_list_of_layers_to_prune,
                the_list_of_layers_to_compute_Distance, loss_function, device,class_num,the_samplesize_for_compute_distance=2,class_num_for_distance=None,num_iterations=1)
    k_list = get_k_list(results,   the_list_of_layers_to_prune,0.05)

    pruned_model_skeleton = pruned_structure(model=model,named_modules_indices=the_list_of_layers_to_prune,k_list=k_list,example_inputs=next(iter(prune_datasetloader))[0],align_residual_add=True,verbose=True,strict_forward_check=True,)
    pruned_model,report = Generate_model_after_pruning(pruned_model_skeleton,model,
                                 'test_pruned_model.pht',
                                 results,k_list,
                                 the_list_of_layers_to_prune,example_inputs=next(iter(prune_datasetloader))[0],finetune_pruned=True,finetune_epochs=10,finetunedata=fortestvaldata,valdata=fortestvaldata)
    print(report)