// Slidev theme entry
import './styles.css'

export default {
  layouts: {
    default: () => import('./layouts/default.vue'),
    'image-left': () => import('./layouts/image-left.vue'),
    'image-right': () => import('./layouts/image-right.vue')
  }
}
