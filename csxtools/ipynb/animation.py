from matplotlib import animation
from matplotlib import pyplot as plt
from IPython.display import HTML
from tempfile import NamedTemporaryFile
import base64


def image_stack_to_movie(images, frames=None):

    if frames is None:
        frames = images.shape[0]

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    im = plt.imshow(images[1], vmin=-10, vmax=10, cmap='CMRmap',
                    interpolation='none')
    fig.colorbar(im)
    for item in ([ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(20)

    def animate(i):
        im.set_array(images[i])
        ax.set_title('Frame {}'.format(i), fontsize=24, fontweight='bold')
        return im,

    anim = animation.FuncAnimation(fig, animate, frames=1000,
                                   interval=1, blit=True)
    plt.close(anim._fig)
    return HTML(anim_to_html(anim))


def anim_to_html(anim):
    VIDEO_TAG = """<video controls>
    <source src="data:video/x-m4v;base64,{0}" type="video/mp4">
    Your browser does not support the video tag.
    </video>"""

    if not hasattr(anim, '_encoded_video'):
        with NamedTemporaryFile(suffix='.mp4') as f:
            anim.save(f.name, fps=10, extra_args=['-vcodec', 'libx264',
                                                  '-pix_fmt', 'yuv420p'])
            video = open(f.name, "rb").read()
        anim._encoded_video = base64.b64encode(video)
    return VIDEO_TAG.format(anim._encoded_video.decode("utf-8"))
