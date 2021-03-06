#from redner, improving the function to save out the obj file and the optimized material maps
import os
import pyredner
from typing import Union
from utils.args import get_args


arg = get_args()

file_name = arg.folder
optimized_results = os.path.join(file_name,'results/optimized/')
if(os.path.isdir(optimized_results)!=True):
    os.mkdir(optimized_results)


def save_material(m: pyredner.Material,
             filename: str):
    if filename[-4:] != '.mtl':
        filename = filename + '.mtl'
    path = os.path.dirname(filename)

    directory = os.path.dirname(filename)
    if directory != '' and not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, 'w') as f:
        f.write('newmtl mtl_1\n')

        if m.diffuse_reflectance is not None:
            texels = m.diffuse_reflectance.texels
            if len(texels.size()) == 1:
                f.write('Kd {} {} {}\n'.format(texels[0], texels[1], texels[2]))
            else:
                f.write('map_Kd Kd_texels.png\n')
                pyredner.imwrite(texels.data.cpu(), optimized_results + '/Kd_texels.png')
        
        if m.specular_reflectance is not None:
            texels = m.specular_reflectance.texels
            if len(texels.size()) == 1:
                f.write('Ks {} {} {}\n'.format(texels[0], texels[1], texels[2]))
            else:
                f.write('map_Ks Ks_texels.png\n')
                pyredner.imwrite(texels.data.cpu(), optimized_results + '/Ks_texels.png')
                
        if m.roughness is not None:
            texels = m.roughness.texels
            if len(texels.size()) == 1:
                f.write('Pr {} {} {}\n'.format(texels[0], texels[1], texels[2]))
            else:
                f.write('map_Ns Ns_texels.png\n')
                pyredner.imwrite(texels.data.cpu(), optimized_results + '/Ns_texels.png')
                

                

def save_obj_file(shape: Union[pyredner.Object, pyredner.Shape],
             filename: str,
             flip_tex_coords = True):


    if filename[-4:] != '.obj':
        filename = filename + '.obj'
    path = os.path.dirname(filename)
    name = os.path.basename(filename)[:-4]

    save_material(m=shape.material, filename=filename[:-4])

    directory = os.path.dirname(filename)
    if directory != '' and not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, 'w') as f:
        f.write('mtllib {}.mtl\n'.format(name))

        vertices = shape.vertices.data.cpu().numpy()
        uvs = shape.uvs.cpu().numpy() if shape.uvs is not None else None
        normals = shape.normals.data.cpu().numpy() if shape.normals is not None else None
        for i in range(vertices.shape[0]):
            f.write('v {} {} {}\n'.format(vertices[i, 0], vertices[i, 1], vertices[i, 2]))
        if uvs is not None:
            for i in range(uvs.shape[0]):
                if flip_tex_coords:
                    f.write('vt {} {}\n'.format(uvs[i, 0], 1 - uvs[i, 1]))
                else:
                    f.write('vt {} {}\n'.format(uvs[i, 0], uvs[i, 1]))
        if normals is not None:
            for i in range(normals.shape[0]):
                f.write('vn {} {} {}\n'.format(normals[i, 0], normals[i, 1], normals[i, 2]))

        f.write('usemtl mtl_1\n')

        indices = shape.indices.data.cpu().numpy() + 1
        uv_indices = shape.uv_indices.data.cpu().numpy() + 1 if shape.uv_indices is not None else None
        normal_indices = shape.normal_indices.data.cpu().numpy() + 1 if shape.normal_indices is not None else None
        for i in range(indices.shape[0]):
            vi = (indices[i, 0], indices[i, 1], indices[i, 2])
            if uv_indices is not None:
                uvi = (uv_indices[i, 0], uv_indices[i, 1], uv_indices[i, 2])
            else:
                if uvs is not None:
                    uvi = vi
                else:
                    uvi = ('', '', '')
            if normal_indices is not None:
                ni = (normal_indices[i, 0], normal_indices[i, 1], normal_indices[i, 2])
            else:
                if normals is not None:
                    ni = vi
                else:
                    ni = ('', '', '')
            if normals is not None:
                f.write('f {}/{}/{} {}/{}/{} {}/{}/{}\n'.format(\
                    vi[0], uvi[0], ni[0],
                    vi[1], uvi[1], ni[1],
                    vi[2], uvi[2], ni[2]))
            elif uvs is not None:
                f.write('f {}/{} {}/{} {}/{}\n'.format(\
                    vi[0], uvi[0],
                    vi[1], uvi[1],
                    vi[2], uvi[2]))
            else:
                f.write('f {} {} {}\n'.format(\
                    vi[0],
                    vi[1],
                    vi[2]))


